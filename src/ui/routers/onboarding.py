# src/ui/routers/onboarding.py
import os
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import get_session
from src.db.models import Tenant, Organization as Org
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates 

# CHANGE THIS IMPORT:
from src.ui.dependencies import get_templates 

load_dotenv()
router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.get("/edit", response_class=HTMLResponse)
async def edit_page(
    tenant_id: int,
    org_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    templates: Jinja2Templates = Depends(get_templates) 
):
    # ... rest of your logic remains the same ...
    tenant = await session.scalar(select(Tenant).where(Tenant.id == tenant_id))
    org = await session.scalar(select(Org).where(Org.id == org_id))
    
    if not tenant or not org:
        return HTMLResponse("<h3>Error: Tenant or Organization not found.</h3>", status_code=404)

    return templates.TemplateResponse("onboarding_edit.html", {"request": request, "tenant": tenant, "org": org})

@router.post("/update")
async def update_page(
    tenant_id: int = Form(...),
    org_id: int = Form(...),
    slug: str = Form(...),
    org_name: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    # Check uniqueness of slug
    existing = await session.scalar(select(Tenant).where(Tenant.slug == slug))
    if existing and existing.id != tenant_id:
        return HTMLResponse("<h3>Error: Slug already taken. Please choose another.</h3>", status_code=400)

    # Update tenant and org
    tenant = await session.scalar(select(Tenant).where(Tenant.id == tenant_id))
    org = await session.scalar(select(Org).where(Org.id == org_id))

    if not tenant or not org:
        return HTMLResponse("<h3>Error: Tenant or Organization not found.</h3>", status_code=404)

    tenant.slug = slug
    org.name = org_name
    await session.commit()

    return RedirectResponse(url=f"/dashboard?tenant_id={tenant_id}", status_code=303)