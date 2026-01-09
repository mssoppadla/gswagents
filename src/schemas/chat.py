# src/schemas/chat.py
from pydantic import BaseModel

class ChatSessionCreate(BaseModel):
    org_id: int

class ChatMessage(BaseModel):
    session_token: str
    org_id: int
    thread_id: str | None = None
    message: str

#Working memoryless agent.
# # src/schemas/chat.py
# from pydantic import BaseModel

# class ChatSessionCreate(BaseModel):
#     org_id: int

# class ChatMessage(BaseModel):
#     session_token: str
#     message: str
