from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.session import get_session
from src.db.models import Tenant, Organization, Widget
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/tenants", tags=["tenants"])

# Pydantic schema for onboarding request
class TenantOnboardingRequest(BaseModel):
    slug: str
    domain: str
    organization_name: str
    logo_url: str | None = None
    theme_color: str | None = None
    chat_logo_url: str | None = None
    welcome_message: str | None = None


@router.post("/", response_model=dict)
async def onboard_tenant(payload: TenantOnboardingRequest, session: AsyncSession = Depends(get_session)):
    # 1. Create organization
    org = Organization(
        slug=payload.slug,
        name=payload.organization_name,
        public_api_key_hash="placeholder_hash",  # TODO: generate securely
        allowed_domain=payload.domain,
        created_at=datetime.utcnow()
    )
    session.add(org)
    await session.flush()  # ensures org.id is available

    # 2. Create tenant linked to org
    tenant = Tenant(
        id=None,  # auto-increment
        slug=payload.slug,
        domain=payload.domain,
        logo_url=payload.logo_url,
        theme_color=payload.theme_color,
        chat_logo_url=payload.chat_logo_url,
        welcome_message=payload.welcome_message,
        created_at=datetime.utcnow()
    )
    session.add(tenant)
    await session.flush()

    # 3. Create default widget for tenant
    widget = Widget(
        org_id=tenant.id,
        position="bottom-right",
        chat_logo_url=payload.chat_logo_url,
        welcome_message=payload.welcome_message,
        created_at=datetime.utcnow()
    )
    session.add(widget)

    await session.commit()

    return {"tenant_id": tenant.id, "organization_id": org.id, "widget_id": widget.id}
