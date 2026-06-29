from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas
import models
from db import get_db
from router.auth import get_current_user

router = APIRouter(prefix="/api/bots", tags=["bots"])

@router.get("", response_model=list[schemas.ChatbotResponse])
def list_bots(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user.chatbots

@router.post("", response_model=schemas.ChatbotResponse)
def create_bot(bot: schemas.ChatbotCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_bot = models.Chatbot(
        owner_id=current_user.id,
        company_name=bot.company_name,
        bot_name=bot.bot_name
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@router.get("/{bot_id}", response_model=schemas.ChatbotResponse)
def get_bot(bot_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bot = db.query(models.Chatbot).filter(models.Chatbot.id == bot_id, models.Chatbot.owner_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return bot

@router.put("/{bot_id}", response_model=schemas.ChatbotResponse)
def update_bot(bot_id: str, updates: schemas.ChatbotUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bot = db.query(models.Chatbot).filter(models.Chatbot.id == bot_id, models.Chatbot.owner_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
        
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bot, key, value)
        
    db.commit()
    db.refresh(bot)
    return bot
