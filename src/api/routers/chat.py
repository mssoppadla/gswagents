# src/api/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_session
from src.db.models import GuestIdentity
from src.schemas.chat import ChatSessionCreate, ChatMessage

router = APIRouter()

@router.post("/session")
async def start_session(payload: ChatSessionCreate, session: AsyncSession = Depends(get_session)):
    token = str(uuid.uuid4())
    guest = GuestIdentity(org_id=payload.org_id, session_token=token, created_at=datetime.utcnow())
    session.add(guest)
    await session.commit()
    return {"session_token": token}

@router.post("/query")
async def chat_query(payload: ChatMessage, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(GuestIdentity).where(GuestIdentity.session_token == payload.session_token))
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Session not found")

    # Route message to your agent (stubbed here)
    reply = f"Echo: {payload.message}"
    return {"reply": reply}
