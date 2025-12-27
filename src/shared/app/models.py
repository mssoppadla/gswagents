# src/shared/app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    public_api_key_hash = Column(String(255), nullable=False)
    allowed_domain = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    configs = relationship("ConfigTheme", back_populates="organization")
    documents = relationship("Document", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # owner | admin
    workos_user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")

class GuestIdentity(Base):
    __tablename__ = "guest_identities"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    origin = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

class ConfigTheme(Base):
    __tablename__ = "config_themes"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    display_name = Column(String(255), nullable=False)
    logo_url = Column(String(255), nullable=True)
    welcome_message = Column(Text, nullable=True)
    theme_json = Column(Text, nullable=True)
    published = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="configs")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    type = Column(String(50), nullable=False)  # pdf | docx | sheet | text
    url = Column(String(255), nullable=False)
    status = Column(String(50), default="active")  # active | deleted
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="documents")
