from fastapi import FastAPI, Request, HTTPException, Security, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import os

from config import HF_MODEL_ID, RATE_LIMIT_PER_MINUTE, get_bot_name, get_company_name, save_dynamic_config, SUPPORT_EMAIL, SUPPORT_URL
from auth.api_key import verify_api_key
from router.classifier import classify_intent
from router.guardrails import check_guardrails
from router.retriever import retrieve_context
from llm.prompt_builder import build_system_prompt
from llm.inference import generate_response
from ingestion.pdf_parser import parse_pdf_bytes
from ingestion.form_parser import parse_form_data
from ingestion.chunker import chunk_text
from vector_store.chroma_client import add_chunks, clear_all
from keepalive import start_keepalive

app = FastAPI(title="Company Chatbot Engine")

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

@app.post("/chat")
@limiter.limit(RATE_LIMIT_PER_MINUTE)
async def chat(request: Request, body: ChatRequest):
    user_msg = body.message.strip()
    
    # Layer 1 & 2: Guardrails and Intent
    guardrail_block = check_guardrails(user_msg)
    if guardrail_block == "JAILBREAK":
        reply = f"I'm not able to help with that. I'm designed to assist with {COMPANY_NAME} topics only. How can I help you with something related to our services?"
        return {"reply": reply, "source_chunks": [], "confidence": 1.0, "session_id": body.session_id}
    elif guardrail_block == "HARMFUL":
        reply = f"That's not something I'm set up to assist with. Please reach out to {SUPPORT_EMAIL} if you need urgent help."
        return {"reply": reply, "source_chunks": [], "confidence": 1.0, "session_id": body.session_id}
        
    intent = classify_intent(user_msg)
    if intent == "GREETING":
        return {
            "reply": f"Hello! I'm {get_bot_name()}, {get_company_name()}'s virtual assistant. How can I help you today?",
            "source_chunks": [],
            "confidence": 1.0,
            "session_id": body.session_id
        }
    # Layer 3: RAG Retriever
    context_text, source_chunks, confidence = retrieve_context(user_msg, top_k=3)
    if not context_text:
        reply = f"I don't have that specific information available right now. For the most accurate answer, I'd recommend reaching out to our team at {SUPPORT_EMAIL} or visiting {SUPPORT_URL}."
        return {"reply": reply, "source_chunks": [], "confidence": 0.0, "session_id": body.session_id}
        
    # Build prompt and chat history
    sys_prompt = build_system_prompt(context_text)
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

@app.post("/admin/upload-pdf", dependencies=[Security(verify_api_key)])
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    text = parse_pdf_bytes(contents)
    
    # Extract identity
    try:
        from llm.inference import generate_response
        extraction_prompt = f"Extract the primary company name from this text. Also suggest a friendly, professional one-word name for an AI assistant representing this company. Output ONLY two lines in exactly this format:\\nCompany: [Name]\\nBot: [Name]\\n\\nText snippet: {text[:3000]}"
        extraction_msg = [{"role": "user", "content": extraction_prompt}]
        response = generate_response(extraction_msg)
        
        extracted_company = None
        extracted_bot = None
        
        # More robust parsing for smaller models that might add filler text
        for line in response.split('\\n'):
            line_clean = line.strip().lower()
            if 'company:' in line_clean:
                # Find the actual text after 'company:'
                idx = line_clean.find('company:')
                # Extract from the original case-sensitive line
                extracted_company = line[idx + 8:].strip().strip('*').strip('"').strip("'")
            elif 'bot:' in line_clean:
                idx = line_clean.find('bot:')
                extracted_bot = line[idx + 4:].strip().strip('*').strip('"').strip("'")
                
        if extracted_company and extracted_bot:
            save_dynamic_config(extracted_company, extracted_bot)
            print(f"Successfully extracted identity: Bot '{extracted_bot}' for '{extracted_company}'")
        else:
            print(f"Failed to parse identity from LLM response:\\n{response}")
    except Exception as e:
        print(f"Identity extraction failed: {e}")
        
    chunks = chunk_text(text)
    add_chunks(chunks, source_id=file.filename)
    
    company_name = get_company_name()
    bot_name = get_bot_name()
    return {"message": f"Successfully indexed {len(chunks)} chunks from {file.filename}. Identity set to {bot_name} at {company_name}."}

@app.post("/admin/submit-form", dependencies=[Security(verify_api_key)])
async def submit_form(form_data: dict):
    text = parse_form_data(form_data)
    chunks = chunk_text(text)
    add_chunks(chunks, source_id="admin_form")
    return {"message": f"Successfully indexed {len(chunks)} chunks from form"}

@app.delete("/admin/reset", dependencies=[Security(verify_api_key)])
async def reset_knowledge():
    clear_all()
    return {"message": "Knowledge base cleared."}

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return {"error": f"Rate limit exceeded: {exc.detail}"}
