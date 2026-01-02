from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ConfigureWidgetRequest(BaseModel):
    org_id: int
    position: str
    chat_logo_url: str
    welcome_message: str

@router.get("/embed-code")
async def get_embed_code(org_slug: str, welcome_message: str = "Welcome to our chat!"):
    embed = f"""
    <script src='https://chat.zenai.co.in/embed.js?org={org_slug}'></script>
    <script>
      window.chatConfig = {{
        welcomeMessage: "{welcome_message}"
      }};
    </script>
    """
    return {"embed_code": embed}

@router.post("/configure")
async def configure_widget(payload: ConfigureWidgetRequest):
    return {
        "message": f"Widget for org {payload.org_id} configured",
        "position": payload.position,
        "chat_logo": payload.chat_logo_url,
        "welcome_message": payload.welcome_message
    }
