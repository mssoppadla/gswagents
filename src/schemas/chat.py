# src/schemas/chat.py
from pydantic import BaseModel

class ChatSessionCreate(BaseModel):
    org_id: int

class ChatMessage(BaseModel):
    session_token: str
    message: str
