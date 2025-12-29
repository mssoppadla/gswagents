# src/ui/routers/onboarding.py
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






# # ****************** Index page working for this 
# # src/ui/routers/onboarding.py
# import os
# from fastapi import APIRouter, Depends, Form, Request
# from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from src.db.session import get_session
# from src.db.models import Tenant, Organization as Org
# from dotenv import load_dotenv
# from fastapi.templating import Jinja2Templates
# from pathlib import Path

# templates = Jinja2Templates(directory="templates")

# load_dotenv()
# print("✅ onboarding.py loaded")
# router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# @router.get("/edit", response_class=HTMLResponse)
# async def edit_page(
#     tenant_id: int,
#     org_id: int,
#     request: Request,
#     session: AsyncSession = Depends(get_session)
# ):
#     # Fetch tenant and org safely
#     print(f"DEBUG: /onboarding/edit called with tenant_id={tenant_id}, org_id={org_id}")
#     tenant = await session.scalar(select(Tenant).where(Tenant.id == tenant_id))
#     org = await session.scalar(select(Org).where(Org.id == org_id))


# # Debug: log DB results 
#     if tenant: 
#         print(f"DEBUG: Tenant found -> id={tenant.id}, slug={tenant.slug}") 
#     else: 
#         print("DEBUG: Tenant not found") 
    
#     if org: 
#         print(f"DEBUG: Org found -> id={org.id}, name={org.name}") 
#     else: 
#         print("DEBUG: Org not found")
    
    
#     if not tenant or not org:
#         return HTMLResponse("<h3>Error: Tenant or Organization not found.</h3>", status_code=404)

#     # Debug: confirm template rendering 
#     print("DEBUG: Rendering onboarding_edit.html template")

#     return templates.TemplateResponse( "onboarding_edit.html", {"request": request, "tenant": tenant, "org": org} )

# @router.post("/update")
# async def update_page(
#     tenant_id: int = Form(...),
#     org_id: int = Form(...),
#     slug: str = Form(...),
#     org_name: str = Form(...),
#     session: AsyncSession = Depends(get_session)
# ):
#     # Check uniqueness of slug
#     existing = await session.scalar(select(Tenant).where(Tenant.slug == slug))
#     if existing and existing.id != tenant_id:
#         return HTMLResponse("<h3>Error: Slug already taken. Please choose another.</h3>", status_code=400)

#     # Update tenant and org
#     tenant = await session.scalar(select(Tenant).where(Tenant.id == tenant_id))
#     org = await session.scalar(select(Org).where(Org.id == org_id))

#     if not tenant or not org:
#         return HTMLResponse("<h3>Error: Tenant or Organization not found.</h3>", status_code=404)

#     tenant.slug = slug
#     org.name = org_name
#     await session.commit()

#     return RedirectResponse(url=f"/dashboard?tenant_id={tenant_id}", status_code=303)



#__________________________________
# src/ui/routers/onboarding.py
# from fastapi import APIRouter, Depends, Form
# from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from src.db import get_session
# from src.models import Tenant, Org

# router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# @router.get("/edit", response_class=HTMLResponse)
# async def edit_page(tenant_id: int, org_id: int, session: AsyncSession = Depends(get_session)):
#     tenant = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one()
#     org = (await session.execute(select(Org).where(Org.id == org_id))).scalar_one()

#     return f"""
#     <html>
#       <body>
#         <h2>Welcome, {tenant.display_name}</h2>
#         <form method="post" action="/onboarding/update">
#           <input type="hidden" name="tenant_id" value="{tenant.id}">
#           <input type="hidden" name="org_id" value="{org.id}">
#           <label>Slug (unique business name):</label>
#           <input type="text" name="slug" value="{tenant.slug}">
#           <br>
#           <label>Org name:</label>
#           <input type="text" name="org_name" value="{org.name}">
#           <br>
#           <button type="submit">Save</button>
#         </form>
#       </body>
#     </html>
#     """

# @router.post("/update")
# async def update_page(tenant_id: int = Form(...), org_id: int = Form(...),
#                       slug: str = Form(...), org_name: str = Form(...),
#                       session: AsyncSession = Depends(get_session)):
#     # Check uniqueness of slug
#     existing = (await session.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none()
#     if existing and existing.id != tenant_id:
#         return HTMLResponse("<h3>Error: Slug already taken. Please choose another.</h3>")

#     tenant = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one()
#     tenant.slug = slug
#     org = (await session.execute(select(Org).where(Org.id == org_id))).scalar_one()
#     org.name = org_name
#     await session.commit()

#     return RedirectResponse(url=f"/dashboard?tenant_id={tenant_id}", status_code=303)
