import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------------------
# Load DATABASE_URL from environment
# Example:
#   postgresql+asyncpg://zenai_user:Password@xpgsqlagent.postgres.database.azure.com:5432/zenai_db
# -------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, echo=False, future=True) 
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# -------------------------------------------------------------------
# Configure SSL for Azure PostgreSQL
# asyncpg does not support ?sslmode=require, so we pass an SSL context
# -------------------------------------------------------------------
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# -------------------------------------------------------------------
# Create async SQLAlchemy engine
# -------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": ssl_context},
    echo=False,          # set True for debugging SQL queries
    future=True
)

# -------------------------------------------------------------------
# Session factory
# -------------------------------------------------------------------
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# -------------------------------------------------------------------
# Dependency for FastAPI
# -------------------------------------------------------------------
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
