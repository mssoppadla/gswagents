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
import logging
load_dotenv()
 
# prefix="/auth/google", removed this parameter inside the APIRouter() to match main.py
router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
print("[DEBUG]: Entered into Auth.py")
# print("Debug: GOOGLE_CLIENT_ID:", GOOGLE_CLIENT_ID)
# print("Debug: GOOGLE_REDIRECT_URI:", GOOGLE_REDIRECT_URI)
# print("Debug: GOOGLE_CLIENT_SECRET:", GOOGLE_CLIENT_SECRET)

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
    try:
        resp.raise_for_status()
    except Exception:
        print("[DEBUG] inside exchange tokens code for tokens definition- Google token response:", resp.text)
        raise
    return resp.json()

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

@router.get("/google/login")
async def google_login():
    print ("[DEBUG]: Inside google_login()/auth/google/login")
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&scope=openid+email+profile"
        
    )
    #f"&access_type=offline&prompt=consent" removed from the above
    #https://www.googleapis.com/auth/documents.readonly
    print("[DEBUG2.0.6]: end of Google OAuth LOGIN AND URL is:", url)
    print("Debug: GOOGLE_CLIENT_ID from variables:", GOOGLE_CLIENT_ID)
    print("[DEBUG]: GOOGLE_REDIRECT_URI from variables:", GOOGLE_REDIRECT_URI)
    response = RedirectResponse(url=url)
    print("[DEBUG] Response headers:", response.headers)
    print("[DEBUG] Response status:", response.status_code)
    print("[DEBUG] Response location:", response.headers.get("location"))
    logger.debug("from logger RedirectResponse created with location=%s status=%s", response.headers.get("location"), response.status_code)
    return response

@router.get("/google/callback")
async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
    print("[DEBUG]: Inside google_callback()/auth/google/callback")
    logger.debug("Inside google_callback from logger()")

    try:
        print("[DEBUG]: token exchange is called")
        tokens = await exchange_code_for_tokens(code)
        id_token = tokens.get("id_token")

        if not id_token:
            logger.error("No id_token in Google response: %s", tokens)
            return RedirectResponse(url="/error?reason=no_id_token")

        # Decode ID token
        user_info = decode_id_token(id_token)

        # Fetch full profile
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            resp.raise_for_status()
            profile = resp.json()

        email = profile.get("email") or user_info.get("email")
        name = profile.get("name") or user_info.get("name")

        if not email:
            logger.error("No email found in Google response")
            return RedirectResponse(url="/error?reason=no_email")

        print("[DEBUG]: decoded token:", user_info)

    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return RedirectResponse(url="/error?reason=oauth_failed")

    # Tenant
    tenant = await session.scalar(select(Tenant).where(Tenant.slug == email))
    if not tenant:
        print("[DEBUG]: Tenant not found, creating new tenant for email:", email)
        tenant = Tenant(
            slug=email,
            domain=email.split("@")[1],
        )
        session.add(tenant)
        await session.flush()

    Organization
    org = await session.scalar(
        select(Org).where(Org.tenant_id == tenant.id, Org.slug == email)
    )
    
    # org = await session.scalar(
    # select(Org).where((Org.tenant_id == tenant.id) & (Org.slug == email))
    # )

    
    if not org:
        raw_key = secrets.token_urlsafe(32)
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

        # Store raw key securely
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

    # Secrets upsert
    async def upsert_secret(key, value):
        if not value:
            return
        existing = await session.scalar(
            select(Secret).where(
                Secret.tenant_id == tenant.id,
                Secret.org_id == org.id,
                Secret.key == key
            )
        )
        if existing:
            existing.value = encrypt(value)
        else:
            session.add(Secret(
                tenant_id=tenant.id,
                org_id=org.id,
                key=key,
                value=encrypt(value),
            ))

    await upsert_secret("google_access_token", tokens.get("access_token"))
    await upsert_secret("google_refresh_token", tokens.get("refresh_token"))
    await upsert_secret("google_id_token", tokens.get("id_token"))
    await upsert_secret("google_scope", tokens.get("scope"))
    await upsert_secret("google_token_type", tokens.get("token_type"))

    await session.commit()
    return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")


# @router.get("/google/callback")
# async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
#     print ("[DEBUG]: Inside google_callback()/auth/google/callback")
#     logger.debug("Inside google_callback from logger()")
    
#     try:
#         print ("[DEBUG]: tocken excchange is called ")
#         logger.debug("kicking off  tocken exchange")
#         # tokens = await exchange_code_for_tokens(code)
#         # user_info = decode_id_token(tokens["id_token"])
#         # print("[DEBUG]: Tokens received:", tokens)
 
#         tokens = await exchange_code_for_tokens(code)
#         id_token = tokens.get("id_token")

#         # Decode ID token (basic claims)
#         user_info = decode_id_token(id_token)

#         # Fetch full profile from Google userinfo endpoint
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(
#                 "https://openidconnect.googleapis.com/v1/userinfo",
#                 headers={"Authorization": f"Bearer {tokens['access_token']}"}
#             )
#             resp.raise_for_status()
#             profile = resp.json()

#         # Merge claims
#         email = profile.get("email") or user_info.get("email")
#         name = profile.get("name") or user_info.get("name")

#         if not email:
#             logger.error("No email found in Google response")
#             return RedirectResponse(url="/error?reason=no_email")

#         print("[DEBUG]:decoded token:", user_info)
#     except Exception as e:
#         logger.error(f"Token exchange failed: {e}")
#         return RedirectResponse(url="/error?reason=oauth_failed")

#     id_token = tokens.get("id_token")
#     if not id_token:
#         logger.error("No id_token in Google response: %s", tokens)
#         return RedirectResponse(url="/error?reason=no_id_token")
#     user_info = decode_id_token(id_token)


#     #user_info = decode_id_token(tokens["id_token"])
#     email, name = user_info["email"], user_info.get("name")

#     # Tenant
#     tenant = await session.scalar(select(Tenant).where(Tenant.slug == email))
#     if not tenant:
#         print("[DEBUG]: Tenant not found so Creating new tenant for email:")
#         tenant = Tenant(
#             slug=email,
#             domain=email.split("@")[1],  # mandatory
#         )
#         session.add(tenant)
#         await session.flush()

#     # Org
#     org = await session.scalar(select(Org).where(Org.tenant_id == tenant.id))
#     if not org:
#         raw_key = secrets.token_urlsafe(32)  # generate random API key
#         api_key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
#         org = Org(
#             tenant_id=tenant.id,
#             slug=email,
#             name=email,
#             public_api_key_hash=api_key_hash,
#             allowed_domain=email.split("@")[1]
#         )
#         session.add(org)
#         await session.flush()

#         # Store raw key securely in secrets
#         session.add(Secret(
#             tenant_id=tenant.id,
#             org_id=org.id,
#             key="public_api_key",
#             value=encrypt(raw_key),
#         ))

#     # User
#     user = await session.scalar(select(User).where(User.email == email))
#     if not user:
#         user = User(org_id=org.id, email=email, hashed_password=None)
#         session.add(user)
#         await session.flush()

#     # Google tokens in secrets
#     def add_secret(key, value):
#         if value:
#             session.add(Secret(
#                 tenant_id=tenant.id,
#                 org_id=org.id,
#                 key=key,
#                 value=encrypt(value),
#             ))

#     add_secret("google_access_token", tokens.get("access_token"))
#     add_secret("google_refresh_token", tokens.get("refresh_token"))
#     add_secret("google_id_token", tokens.get("id_token"))
#     add_secret("google_scope", tokens.get("scope"))
#     add_secret("google_token_type", tokens.get("token_type"))

#     await session.commit()
#     return RedirectResponse(url=f"/onboarding/edit?tenant_id={tenant.id}&org_id={org.id}")

