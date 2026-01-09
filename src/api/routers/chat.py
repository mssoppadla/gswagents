#src/api/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid
import logging

from src.db.session import get_session
from src.db.models import GuestIdentity
from src.schemas.chat import ChatSessionCreate, ChatMessage
from agent_framework import ChatAgent
from src.api.dependencies import get_agent

router = APIRouter()

@router.post("/session")
async def start_session(payload: ChatSessionCreate, session: AsyncSession = Depends(get_session)):
    token = str(uuid.uuid4())
    guest = GuestIdentity(org_id=payload.org_id, session_token=token, created_at=datetime.utcnow())
    session.add(guest)
    await session.commit()
    logging.info("Session request received:" + str(guest))
    return {"session_token": token}

@router.post("/query/stream")
async def chat_query_stream(
    payload: ChatMessage,
    request: Request,
    session: AsyncSession = Depends(get_session),
    chat_agent: ChatAgent = Depends(get_agent)
):
    logging.info(" Received request from front end widget:" + str(payload))
    result = await session.execute(
        select(GuestIdentity).where(GuestIdentity.session_token == payload.session_token)
    )
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Session not found")

    async def token_generator():
        async for update in chat_agent.run_stream(payload.message):
            yield f"data: {update.text}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream"
    }

    return StreamingResponse(token_generator(), headers=headers)

@router.post("/query")
async def chat_query(
    payload: ChatMessage,
    session: AsyncSession = Depends(get_session),
    chat_agent: ChatAgent = Depends(get_agent)
):
    result = await session.execute(
        select(GuestIdentity).where(GuestIdentity.session_token == payload.session_token)
    )
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Session not found")

    response = await chat_agent.run(payload.message)
    return {"reply": response.text}











# # src/api/routers/chat.py
# from fastapi import APIRouter, Depends, HTTPException, Request
# from fastapi.responses import StreamingResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from datetime import datetime
# import uuid

# from src.db.session import get_session
# from src.db.models import GuestIdentity
# from src.schemas.chat import ChatSessionCreate, ChatMessage
# from agent_framework import ChatAgent
# from src.api.dependencies import get_agent

# router = APIRouter()

# @router.post("/session")
# async def start_session(payload: ChatSessionCreate, session: AsyncSession = Depends(get_session)):
#     token = str(uuid.uuid4())
#     guest = GuestIdentity(org_id=payload.org_id, session_token=token, created_at=datetime.utcnow())
#     session.add(guest)
#     await session.commit()
#     return {"session_token": token}

# ##############################
# @router.post("/query/stream")
# async def chat_query_stream(
#     payload: ChatMessage,
#     request: Request,
#     session: AsyncSession = Depends(get_session),
#     chat_agent: ChatAgent = Depends(get_agent)
# ):
#     # Validate session
#     result = await session.execute(
#         select(GuestIdentity).where(GuestIdentity.session_token == payload.session_token)
#     )
#     guest = result.scalar_one_or_none()
#     if not guest:
#         print("[ERROR]: Session not found for token:", payload.session_token)
#         raise HTTPException(status_code=404, detail="Session not found")

#     # Generator that yields agent tokens
#     async def token_generator():
#         async for update in chat_agent.run_stream(payload.message):
#             yield f"data: {update.text}\n\n"

#     # SSE headers
#     headers = {
#         "Cache-Control": "no-cache",
#         "Connection": "keep-alive",
#         "Content-Type": "text/event-stream"
#     }

#     return StreamingResponse(token_generator(), headers=headers)

# ###############################

# @router.post("/query")
# async def chat_query(
#     payload: ChatMessage,
#     session: AsyncSession = Depends(get_session),
#     chat_agent: ChatAgent = Depends(get_agent)   # ✅ inject agent
# ):
#     result = await session.execute(
#         select(GuestIdentity).where(GuestIdentity.session_token == payload.session_token)
#     )
#     guest = result.scalar_one_or_none()
#     if not guest:
#         raise HTTPException(status_code=404, detail="Session not found")

#     # ✅ Call the agent instead of echo
#     response = await chat_agent.run(payload.message)
#     return {"reply": response.text}
