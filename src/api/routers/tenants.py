from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from src.db.session import get_session
from src.db.models import Tenant
from src.schemas.tenants import TenantCreate, TenantUpdate

router = APIRouter()

@router.post("/")
async def onboard_tenant(payload: TenantCreate, session: AsyncSession = Depends(get_session)):
    tenant = Tenant(
        slug=payload.slug,
        domain=payload.domain,
        created_at=datetime.utcnow(),
    )
    session.add(tenant)
    await session.commit()
    return {"tenant_id": tenant.id}

@router.patch("/{tenant_id}")
async def update_tenant(tenant_id: int, payload: TenantUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        return {"error": f"Tenant {tenant_id} not found"}

    if payload.logo_url is not None:
        tenant.logo_url = payload.logo_url
    if payload.theme_color is not None:
        tenant.theme_color = payload.theme_color
    if payload.chat_logo_url is not None:
        tenant.chat_logo_url = payload.chat_logo_url
    if payload.welcome_message is not None:
        tenant.welcome_message = payload.welcome_message

    await session.commit()
    return {"tenant_id": tenant.id, "updated": True}
