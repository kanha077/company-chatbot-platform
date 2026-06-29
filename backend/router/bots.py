from fastapi import APIRouter, Depends, HTTPException, status
import schemas
from router.auth import get_current_user
from firebase_config import db
import uuid

router = APIRouter(prefix="/api/bots", tags=["bots"])

@router.get("", response_model=list[schemas.ChatbotResponse])
def list_bots(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    docs = db.collection("chatbots").where("owner_id", "==", user_id).stream()
    bots = [doc.to_dict() for doc in docs]
    return bots

@router.post("", response_model=schemas.ChatbotResponse)
def create_bot(bot: schemas.ChatbotCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    bot_id = str(uuid.uuid4())
    bot_data = {
        "id": bot_id,
        "owner_id": user_id,
        "company_name": bot.company_name,
        "bot_name": bot.bot_name,
        "system_prompt": "",
        "primary_color": "#2563eb"
    }
    db.collection("chatbots").document(bot_id).set(bot_data)
    return bot_data

@router.get("/{bot_id}", response_model=schemas.ChatbotResponse)
def get_bot(bot_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    doc = db.collection("chatbots").document(bot_id).get()
    if not doc.exists or doc.to_dict().get("owner_id") != user_id:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return doc.to_dict()

@router.put("/{bot_id}", response_model=schemas.ChatbotResponse)
def update_bot(bot_id: str, updates: schemas.ChatbotUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    doc_ref = db.collection("chatbots").document(bot_id)
    doc = doc_ref.get()
    
    if not doc.exists or doc.to_dict().get("owner_id") != user_id:
        raise HTTPException(status_code=404, detail="Chatbot not found")
        
    update_data = updates.dict(exclude_unset=True)
    if update_data:
        doc_ref.update(update_data)
        
    return doc_ref.get().to_dict()
