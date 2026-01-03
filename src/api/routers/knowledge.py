# src/api/routers/knowledge.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from src.db.session import get_session
from src.db.models import KnowledgeBase, Document
from src.schemas.knowledge import KnowledgeBaseCreate, DocumentCreate

router = APIRouter()

@router.post("/bases", summary="Create a new knowledge base")
async def create_knowledge_base(payload: KnowledgeBaseCreate, session: AsyncSession = Depends(get_session)):
    kb = KnowledgeBase(
        tenant_id=payload.tenant_id,
        org_id=payload.org_id,
        name=payload.name,
        created_at=datetime.utcnow()
    )
    session.add(kb)
    await session.commit()
    await session.refresh(kb)
    return {"kb_id": kb.id, "name": kb.name}

@router.post("/attachments", summary="Attach a document to a knowledge base")
async def attach_document(payload: DocumentCreate, session: AsyncSession = Depends(get_session)):
    # Ensure KB exists
    result = await session.execute(select(KnowledgeBase).where(KnowledgeBase.id == payload.kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    doc = Document(
        org_id=payload.org_id,
        kb_id=payload.kb_id,
        title=payload.title,
        content=payload.content,
        source_type=payload.source_type,
        external_id=payload.external_id,
        ingest_status="succeeded",
        created_at=datetime.utcnow()
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return {"document_id": doc.id, "title": doc.title, "status": doc.ingest_status}
