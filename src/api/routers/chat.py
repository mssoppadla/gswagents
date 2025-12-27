from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
async def chat_query():
    return {"response": "Hello from chat"}
