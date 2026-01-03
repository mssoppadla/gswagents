from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import uuid

from src.db.session import get_session
from src.db.models import GuestIdentity

router = APIRouter()

@router.post("/session", summary="Create guest chat session")
async def create_guest_session(org_id: int, session: AsyncSession = Depends(get_session)):
    """
    Create a new guest session for a visitor to an organization's chat widget.
    Returns a unique session token and expiry.
    """
    # Generate a unique token
    token = str(uuid.uuid4())
    expires_in = 3600  # seconds (1 hour)

    # Persist guest identity
    guest = GuestIdentity(
        org_id=org_id,
        session_token=token,
        created_at=datetime.utcnow()
    )
    session.add(guest)
    await session.commit()

    return {"token": token, "expires_in": expires_in}

@router.get("/session/{token}", summary="Validate guest session")
async def validate_guest_session(token: str, session: AsyncSession = Depends(get_session)):
    """
    Validate that a guest session exists for the given token.
    """
    result = await session.execute(select(GuestIdentity).where(GuestIdentity.session_token == token))
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest session not found")
    return {"token": token, "valid": True, "org_id": guest.org_id}
