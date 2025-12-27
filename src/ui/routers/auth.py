from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register_owner(email: str, password: str):
    # TODO: integrate with WorkOS or your identity provider
    return {"message": f"Business owner {email} registered"}

@router.post("/login")
async def login_owner(email: str, password: str):
    # TODO: validate credentials, issue JWT
    return {"message": f"Business owner {email} logged in"}

@router.post("/logout")
async def logout_owner():
    return {"message": "Business owner logged out"}
