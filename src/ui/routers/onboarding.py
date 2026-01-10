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
from typing import List
from fastapi import Form, File, UploadFile

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
    slug: Optional[str] = Form(...),
    org_name: Optional[str] = Form(...),
    subscription: Optional[str] = Form(...),
    agent_instructions: Optional[str] = Form(...),
    temperature: Optional[float] = Form(...),
    upload_files: Optional[List[UploadFile]] = File(None),   # multiple files
    google_urls: Optional[List[str]] = Form(None),           # multiple URLs
    session: AsyncSession = Depends(get_session)
):
    # Check uniqueness of slug
    existing = await session.scalar(select(Tenant).where(Tenant.slug == slug))
    if existing and existing.id != tenant_id:
        return HTMLResponse("<h3>Error: Slug already taken. Please choose another.</h3>", status_code=400)

    # Fetch tenant and org
    tenant = await session.scalar(select(Tenant).where(Tenant.id == tenant_id))
    org = await session.scalar(select(Org).where(Org.id == org_id))

    if not tenant or not org:
        return HTMLResponse("<h3>Error: Tenant or Organization not found.</h3>", status_code=404)

    # Update tenant and org with new fields
    tenant.slug = slug
    #tenant.subscription = subscription
    #tenant.agent_instructions = agent_instructions
    #tenant.temperature = temperature
    org.name = org_name

    # Handle uploaded files (store them somewhere or save metadata)
    if upload_files:
        for file in upload_files:
            contents = await file.read()
            # TODO: save contents to storage or DB
            # e.g., save to blob storage or persist file metadata

    # Handle Google URLs (store them in DB or config)
    if google_urls:
        # TODO: persist list of URLs for this tenant/org
        pass

    await session.commit()

    return RedirectResponse(url=f"/dashboard?tenant_id={tenant_id}", status_code=303)
