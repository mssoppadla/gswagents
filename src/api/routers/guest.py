from fastapi import APIRouter

router = APIRouter()

@router.post("/session")
async def create_guest_session():
    return {"token": "guest-jwt", "expires_in": 3600}
