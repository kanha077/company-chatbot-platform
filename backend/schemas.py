from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatbotCreate(BaseModel):
    company_name: str
    bot_name: str

class ChatbotUpdate(BaseModel):
    company_name: Optional[str] = None
    bot_name: Optional[str] = None
    system_prompt: Optional[str] = None
    primary_color: Optional[str] = None

class ChatbotResponse(BaseModel):
    id: str
    owner_id: int
    company_name: str
    bot_name: str
    system_prompt: str
    primary_color: str
    class Config:
        from_attributes = True
