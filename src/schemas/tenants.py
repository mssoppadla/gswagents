from pydantic import BaseModel
from typing import Optional

class TenantCreate(BaseModel):
    slug: str
    domain: str

class TenantUpdate(BaseModel):
    logo_url: Optional[str] = None
    theme_color: Optional[str] = None
    chat_logo_url: Optional[str] = None
    welcome_message: Optional[str] = None
