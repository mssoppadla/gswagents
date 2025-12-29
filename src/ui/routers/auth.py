# src/ui/routers/auth.py
# src/ui/routers/auth.py
import os, httpx, jwt
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session
from src.db.models import Tenant, Organization as Org, User, Secret
from dotenv import load_dotenv 
import hashlib, secrets
from cryptography.fernet import Fernet   # 👈 added for encryption

load_dotenv()

# prefix="/auth/google", removed this parameter inside the APIRouter() to match main.py
router = APIRouter(tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Load Fernet key from environment (generate once and store securely)
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    # For local dev, generate a key if missing (⚠️ do not use this in prod)
    FERNET_KEY = Fernet.generate_key()
fernet = Fernet(FERNET_KEY)

def encrypt(value: str) -> str:
    """Encrypt a string using Fernet symmetric encryption."""
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    """Decrypt a string using Fernet symmetric encryption."""
    return fernet.decrypt(value.encode()).decode()

def decode_id_token(id_token: str):
    # Decode JWT without verifying signature (for local dev)
    return jwt.decode(id_token, options={"verify_signature": False})

async def exchange_code_for_tokens(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
    resp.raise_for_status()
    return resp.json()

@router.get("/google/login")
async def google_login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid email profile https://www.googleapis.com/auth/documents.readonly"
        f"&access_type=offline&prompt=consent"
    )
    print("Google OAuth URL:", url)
    return RedirectResponse(url=url)

@router.get("/google/callback")
async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
    tokens = await exchange_code_for_tokens(code)
    user_info = decode_id_token(tokens["id_token"])
    email, name = user_info["email"], user_info.get("name")

    # Tenant
    tenant = await session.scalar(select(Tenant).where(Tenant.slug == email))
    if not tenant:
        tenant = Tenant(
            slug=email,
            domain=email.split("@")[1],  # mandatory
        )
        session.add(tenant)
        await session.flush()

    # Org
    org = await session.scalar(select(Org).where(Org.tenant_id == tenant.id))
    if not org:
        raw_key = secrets.token_urlsafe(32)  # generate random API key
        api_key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        org = Org(
            tenant_id=tenant.id,
            slug=email,
            name=email,
            public_api_key_hash=api_key_hash,
            allowed_domain=email.split("@")[1]
        )
        session.add(org)
        await session.flush()

        # Store raw key securely in secrets
        session.add(Secret(
            tenant_id=tenant.id,
            org_id=org.id,
            key="public_api_key",
            value=encrypt(raw_key),
        ))

    # User
    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        user = User(org_id=org.id, email=email, hashed_password=None)
        session.add(user)
        await session.flush()

    # Google tokens in secrets
    def add_secret(key, value):
        if value:
            session.add(Secret(
                tenant_id=tenant.id,
                org_id=org.id,
                key=key,
                value=encrypt(value),
            ))

    add_secret("google_access_token", tokens.get("access_token"))
    add_secret("google_refresh_token", tokens.get("refresh_token"))
    add_secret("google_id_token", tokens.get("id_token"))
    add_secret("google_scope", tokens.get("scope"))
    add_secret("google_token_type", tokens.get("token_type"))

    await session.commit()
    return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")










#--------------------------------------
# import os, httpx, jwt
# from fastapi import APIRouter, Depends
# from fastapi.responses import RedirectResponse
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.db.session import get_session
# from src.db.models import Tenant, Organization as Org, User, Secret
# from dotenv import load_dotenv 
# import hashlib,secrets
# load_dotenv()

# # prefix="/auth/google", removed this parameter inside the APIRouter() to match main.py
# router = APIRouter(tags=["auth"])

# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# def decode_id_token(id_token: str):
#     # Decode JWT without verifying signature (for local dev)
#     return jwt.decode(id_token, options={"verify_signature": False})


# async def exchange_code_for_tokens(code: str):
#     token_url = "https://oauth2.googleapis.com/token"
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(token_url, data={
#             "code": code,
#             "client_id": GOOGLE_CLIENT_ID,
#             "client_secret": GOOGLE_CLIENT_SECRET,
#             "redirect_uri": GOOGLE_REDIRECT_URI,
#             "grant_type": "authorization_code",
#         })
#     resp.raise_for_status()
#     return resp.json()


# @router.get("/google/login")
# async def google_login():
#     url = (
#         "https://accounts.google.com/o/oauth2/v2/auth"
#         f"?client_id={GOOGLE_CLIENT_ID}"
#         f"&redirect_uri={GOOGLE_REDIRECT_URI}"
#         f"&response_type=code"
#         f"&scope=openid email profile https://www.googleapis.com/auth/documents.readonly"
#         f"&access_type=offline&prompt=consent"
#     )
#     print("Google OAuth URL:", url) # 👈 add this line
#     return RedirectResponse(url=url)

# # src/ui/routers/auth.py
# @router.get("/google/callback")
# async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
#     tokens = await exchange_code_for_tokens(code)
#     user_info = decode_id_token(tokens["id_token"])
#     email, name = user_info["email"], user_info.get("name")

#     # Tenant
#     tenant = await session.scalar(select(Tenant).where(Tenant.slug == email))
#     if not tenant:
#         tenant = Tenant(
#             slug=email,
#             domain=email.split("@")[1],  # mandatory
#         )
#         session.add(tenant)
#         await session.flush()

    # Org
#-----------------------
    # Org
    org = await session.scalar(select(Org).where(Org.tenant_id == tenant.id))
    if not org:
        raw_key = secrets.token_urlsafe(32)  # generate random API key
        api_key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        org = Org(
            tenant_id=tenant.id,
            slug=email,
            name=email,
            public_api_key_hash=api_key_hash,
            allowed_domain=email.split("@")[1]
        )
        session.add(org)
        await session.flush()

        # Store raw key securely in secrets
        session.add(Secret(
            tenant_id=tenant.id,
            org_id=org.id,
            key="public_api_key",
            value=encrypt(raw_key),
        ))

    # User
    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        user = User(org_id=org.id, email=email, hashed_password=None)
        session.add(user)
        await session.flush()

    # Google tokens in secrets
    def add_secret(key, value):
        if value:
            session.add(Secret(
                tenant_id=tenant.id,
                org_id=org.id,
                key=key,
                value=encrypt(value),
            ))

    add_secret("google_access_token", tokens.get("access_token"))
    add_secret("google_refresh_token", tokens.get("refresh_token"))
    add_secret("google_id_token", tokens.get("id_token"))
    add_secret("google_scope", tokens.get("scope"))
    add_secret("google_token_type", tokens.get("token_type"))

    await session.commit()
    return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")


#---------------------
    
    #backup before changing for db update
    # org = await session.scalar(select(Org).where(Org.tenant_id == tenant.id))
    # if not org:
    #     org = Org(tenant_id=tenant.id, slug=email, name=email)
    #     session.add(org)
    #     await session.flush()

    # User
    # user = await session.scalar(select(User).where(User.emails == email))
    # if not user:
    #     user = User(
    #         tenant_id=tenant.id,
    #         org_id=org.id,
    #         emails=email,
    #         position=name,  # using position for display_name
    #         hashed_password=None,
    #     )
    #     session.add(user)
    #     await session.flush()

    # # Secrets
    # def add_secret(key, value):
    #     if value:
    #         session.add(Secret(
    #             tenant_id=tenant.id,
    #             org_id=org.id,
    #             name=email,  # workaround for user linkage
    #             key=key,
    #             value=encrypt(value),
    #         ))

    # add_secret("google_access_token", tokens.get("access_token"))
    # add_secret("google_refresh_token", tokens.get("refresh_token"))
    # add_secret("google_id_token", tokens.get("id_token"))
    # add_secret("google_scope", tokens.get("scope"))
    # add_secret("google_token_type", tokens.get("token_type"))

    # await session.commit()
    
    # return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")














# @router.get("/callback")
# async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
#     # Exchange code for tokens
#     token_url = "https://oauth2.googleapis.com/token"
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(token_url, data={
#             "code": code,
#             "client_id": GOOGLE_CLIENT_ID,
#             "client_secret": GOOGLE_CLIENT_SECRET,
#             "redirect_uri": GOOGLE_REDIRECT_URI,
#             "grant_type": "authorization_code",
#         })
#     resp.raise_for_status()
#     tokens = resp.json()

#     # Decode id_token for onboarding info
#     user_info = jwt.decode(tokens["id_token"], options={"verify_signature": False})
#     email = user_info.get("email")
#     name = user_info.get("name")
#     picture = user_info.get("picture")

#     # Tenant = email slug
#     tenant = (await session.execute(
#         select(Tenant).where(Tenant.slug == email)
#     )).scalar_one_or_none()
#     if not tenant:
#         tenant = Tenant(slug=email, display_name=email)
#         session.add(tenant)
#         await session.flush()

#     # Org = default to email
#     org = (await session.execute(
#         select(Org).where(Org.tenant_id == tenant.id)
#     )).scalar_one_or_none()
#     if not org:
#         org = Org(tenant_id=tenant.id, name=email)
#         session.add(org)
#         await session.flush()

#     # User
#     user = (await session.execute(
#         select(User).where(User.email == email)
#     )).scalar_one_or_none()
#     if not user:
#         user = User(tenant_id=tenant.id, org_id=org.id,
#                     email=email, display_name=name, avatar_url=picture)
#         session.add(user)
#         await session.flush()

#     # Secrets (multiple rows per key)
#     def add_secret(key, value):
#         if value:
#             session.add(Secret(tenant_id=tenant.id, org_id=org.id,
#                                user_id=user.id, key=key, value=value))

#     add_secret("google_access_token", tokens.get("access_token"))
#     add_secret("google_refresh_token", tokens.get("refresh_token"))
#     add_secret("google_id_token", tokens.get("id_token"))
#     add_secret("google_scope", tokens.get("scope"))
#     add_secret("google_token_type", tokens.get("token_type"))

#     await session.commit()

#     # Redirect to edit page
#     return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")






# BAckup before changing for db update 28 12 2025 8.59pm
# from fastapi import APIRouter, Request
# from fastapi.responses import RedirectResponse
# import httpx, os
# from dotenv import load_dotenv

# load_dotenv() # reads .env file
# router = APIRouter()

# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_REDIRECT_URI = "http://127.0.0.1:3000/auth/google/callback"  # local dev; change to https://zenai.co.in/auth/google/callback in prod

# @router.get("/google/login")
# async def google_login():
#     google_auth_url = (
#         "https://accounts.google.com/o/oauth2/v2/auth"
#         f"?client_id={GOOGLE_CLIENT_ID}"
#         f"&redirect_uri={GOOGLE_REDIRECT_URI}"
#         f"&response_type=code"
#         f"&scope=openid email profile https://www.googleapis.com/auth/documents.readonly"
#         f"&access_type=offline"
#     )
#     return RedirectResponse(url=google_auth_url)

# @router.get("/google/callback")
# async def google_callback(request: Request, code: str):
#     token_url = "https://oauth2.googleapis.com/token"
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(token_url, data={
#             "code": code,
#             "client_id": GOOGLE_CLIENT_ID,
#             "client_secret": GOOGLE_CLIENT_SECRET,
#             "redirect_uri": GOOGLE_REDIRECT_URI,
#             "grant_type": "authorization_code",
#         })
#     tokens = resp.json()

#     # TODO: store tokens in Secrets table linked to tenant/org
#     return {"tokens": tokens}
