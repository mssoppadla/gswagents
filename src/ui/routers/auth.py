from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register_owner(payload: RegisterRequest):
    return {"message": f"Business owner {payload.email} registered"}

@router.post("/login")
async def login_owner(payload: LoginRequest):
    return {"message": f"Business owner {payload.email} logged in"}

@router.post("/logout")
async def logout_owner():
    return {"message": "Business owner logged out"}
