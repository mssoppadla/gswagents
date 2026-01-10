#src/db/models.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Text
Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(255), nullable=False, unique=True)
    domain = Column(String(255), nullable=False)
    logo_url = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    chat_logo_url = Column(String(255))
    welcome_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    organizations = relationship("Organization", back_populates="tenant")
    widgets = relationship("Widget", back_populates="tenant")
    secrets = relationship("Secret", back_populates="tenant")
    knowledge_bases = relationship("KnowledgeBase", back_populates="tenant")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    public_api_key_hash = Column(String(255), nullable=False)
    allowed_domain = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    tenant = relationship("Tenant", back_populates="organizations")
    users = relationship("User", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    guest_identities = relationship("GuestIdentity", back_populates="organization")
    config_themes = relationship("ConfigTheme", back_populates="organization")


class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    position = Column(String(50))
    chat_logo_url = Column(String(255))
    welcome_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tenant = relationship("Tenant", back_populates="widgets")
    organization = relationship("Organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    organization = relationship("Organization", back_populates="users")


class Secret(Base):
    __tablename__ = "secrets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tenant = relationship("Tenant", back_populates="secrets")
    organization = relationship("Organization")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tenant = relationship("Tenant", back_populates="knowledge_bases")
    organization = relationship("Organization")
    documents = relationship("Document", back_populates="knowledge_base")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    title = Column(String(255))
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # NEW: source metadata (add these)
    source_type = Column(String(50), nullable=True)       # google_doc | google_sheet | url | file
    source_url = Column(String(1024), nullable=True)      # original link
    external_id = Column(String(255), nullable=True)      # Google file ID, etc.
    mime_type = Column(String(255), nullable=True)
    ingest_status = Column(String(50), nullable=True)     # pending | succeeded | failed
    ingest_error = Column(Text, nullable=True)

    organization = relationship("Organization", back_populates="documents")
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


class GuestIdentity(Base):
    __tablename__ = "guest_identities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    session_token = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    organization = relationship("Organization", back_populates="guest_identities")


class ConfigTheme(Base):
    __tablename__ = "config_themes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    theme_name = Column(String(255))
    primary_color = Column(String(50))
    secondary_color = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    organization = relationship("Organization", back_populates="config_themes")

