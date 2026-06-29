from fastapi import FastAPI, Request, HTTPException, Security, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import os

from config import HF_MODEL_ID, RATE_LIMIT_PER_MINUTE, SUPPORT_EMAIL, SUPPORT_URL
from auth.api_key import verify_api_key
from router.classifier import classify_intent
from router.guardrails import check_guardrails
from llm.prompt_builder import build_system_prompt
from llm.inference import generate_response
from ingestion.pdf_parser import parse_pdf_bytes
from ingestion.chunker import chunk_text
from vector_store.chroma_client import add_chunks, clear_all, retrieve_context
from keepalive import start_keepalive
from firebase_config import db
from router import auth, bots

app = FastAPI(title="SaaS Chatbot Engine")

app.include_router(auth.router)
app.include_router(bots.router)

# Start keepalive in background
start_keepalive()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str | None = None

# In-memory session store
SESSION_STORE = {}

def get_history(session_id: str) -> list:
    return SESSION_STORE.get(session_id, {}).get("history", [])

def update_history(session_id: str, role: str, content: str):
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {"history": [], "last_active": time.time()}
    SESSION_STORE[session_id]["history"].append({"role": role, "content": content})
    SESSION_STORE[session_id]["last_active"] = time.time()
    SESSION_STORE[session_id]["history"] = SESSION_STORE[session_id]["history"][-20:]

@app.get("/health")
def health_check():
    return {
        "status": "alive",
        "model": HF_MODEL_ID,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat/{bot_id}")
@limiter.limit(RATE_LIMIT_PER_MINUTE)
async def chat(bot_id: str, request: Request, body: ChatRequest):
    bot_doc = db.collection("chatbots").document(bot_id).get()
    if not bot_doc.exists:
        raise HTTPException(status_code=404, detail="Chatbot not found")
        
    bot = bot_doc.to_dict()
    user_msg = body.message.strip()
    
    # Layer 1 & 2: Guardrails and Intent
    guardrail_block = check_guardrails(user_msg)
    if guardrail_block == "JAILBREAK":
        reply = f"I'm not able to help with that. I'm designed to assist with {bot.get('company_name')} topics only. How can I help you with something related to our services?"
        return {"reply": reply, "source_chunks": [], "confidence": 1.0, "session_id": body.session_id}
    elif guardrail_block == "HARMFUL":
        reply = f"That's not something I'm set up to assist with. Please reach out to {SUPPORT_EMAIL} if you need urgent help."
        return {"reply": reply, "source_chunks": [], "confidence": 1.0, "session_id": body.session_id}
        
    intent = classify_intent(user_msg)
    if intent == "GREETING":
        return {
            "reply": f"Hello! I'm {bot.get('bot_name')}, {bot.get('company_name')}'s virtual assistant. How can I help you today?",
            "source_chunks": [],
            "confidence": 1.0,
            "session_id": body.session_id
        }
        
    # Layer 3: RAG Retriever
    context_text, source_chunks, confidence = retrieve_context(user_msg, top_k=3, bot_id=bot_id)
    if not context_text:
        reply = f"I don't have that specific information available right now. For the most accurate answer, I'd recommend reaching out to our team at {SUPPORT_EMAIL} or visiting {SUPPORT_URL}."
        return {"reply": reply, "source_chunks": [], "confidence": 0.0, "session_id": body.session_id}
        
    # Build prompt and chat history
    sys_prompt = build_system_prompt(context_text)
    if bot.get('system_prompt'):
        sys_prompt += f"\n\nAdditional Instructions: {bot.get('system_prompt')}"
        
    messages = [{"role": "system", "content": sys_prompt}]
    
    history = get_history(body.session_id)
    messages.extend(history)
    messages.append({"role": "user", "content": user_msg})
    
    # Generate LLM response
    reply = generate_response(messages)
    
    # Update history
    update_history(body.session_id, "user", user_msg)
    update_history(body.session_id, "assistant", reply)
    
    return {
        "reply": reply,
        "source_chunks": source_chunks,
        "confidence": confidence,
        "session_id": body.session_id
    }

@app.post("/admin/upload-pdf/{bot_id}")
async def upload_pdf(bot_id: str, file: UploadFile = File(...), current_user: dict = Depends(auth.get_current_user)):
    bot_doc = db.collection("chatbots").document(bot_id).get()
    if not bot_doc.exists or bot_doc.to_dict().get("owner_id") != current_user.get("uid"):
        raise HTTPException(status_code=404, detail="Chatbot not found or unauthorized")
        
    contents = await file.read()
    text = parse_pdf_bytes(contents)
        
    chunks = chunk_text(text)
    add_chunks(chunks, source_id=file.filename, bot_id=bot_id)
    
    return {"message": f"Successfully indexed {len(chunks)} chunks into {bot_doc.to_dict().get('bot_name')} knowledge base."}

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return {"error": f"Rate limit exceeded: {exc.detail}"}
