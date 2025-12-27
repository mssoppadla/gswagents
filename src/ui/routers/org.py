from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CreateOrgRequest(BaseModel):
    name: str
    domain: str
    slug: str
    welcome_message: str

class CustomizeOrgRequest(BaseModel):
    org_id: int
    logo_url: str
    theme_color: str
    chat_logo_url: str
    welcome_message: str

@router.post("/create")
async def create_org(payload: CreateOrgRequest):
    return {"message": f"Organization {payload.name} created with slug {payload.slug}"}

@router.post("/customize")
async def customize_brand(payload: CustomizeOrgRequest):
    return {"message": f"Org {payload.org_id} customized"}
