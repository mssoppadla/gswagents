# src/shared/app/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Load from env (parameterized)
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Async engine with SSL required
engine = create_async_engine(
    POSTGRES_URL,
    echo=False,  # set True for debugging
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()
