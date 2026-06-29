from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    chatbots = relationship("Chatbot", back_populates="owner")

class Chatbot(Base):
    __tablename__ = "chatbots"
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    company_name = Column(String, default="My Company")
    bot_name = Column(String, default="Assistant")
    system_prompt = Column(Text, default="")
    primary_color = Column(String, default="#2563eb")
    
    owner = relationship("User", back_populates="chatbots")
