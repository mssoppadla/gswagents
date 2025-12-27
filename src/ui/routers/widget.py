from fastapi import APIRouter

router = APIRouter()

@router.get("/embed-code")
async def get_embed_code(org_slug: str, welcome_message: str = "Welcome to our chat!"):
    # TODO: fetch org welcome message from DB if available
    embed = f"""
    <script src='https://chat.yourapp.com/embed.js?org={org_slug}'></script>
    <script>
      window.chatConfig = {{
        welcomeMessage: "{welcome_message}"
      }};
    </script>
    """
    return {"embed_code": embed}

@router.post("/configure")
async def configure_widget(org_id: int, position: str, chat_logo_url: str, welcome_message: str):
    # TODO: save widget config with welcome message
    return {
        "message": f"Widget for org {org_id} configured",
        "position": position,
        "chat_logo": chat_logo_url,
        "welcome_message": welcome_message
    }
