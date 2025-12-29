# src/schemas/knowledge.py
from pydantic import BaseModel
from typing import Optional

class KnowledgeBaseCreate(BaseModel):
    tenant_id: int
    org_id: int
    name: str

class DocumentCreate(BaseModel):
    org_id: int
    kb_id: int
    title: str
    content: str
    source_type: Optional[str] = None   # e.g. "google_doc", "url", "file"
    external_id: Optional[str] = None   # e.g. Google Doc ID
