from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Document
from src.services.ingestion.google import fetch_google_doc_content, fetch_google_sheet_content

async def ingest_document_content(doc: Document, session: AsyncSession):
    try:
        content = None
        if doc.source_type == "google_doc":
            content = await fetch_google_doc_content(doc.external_id or "")
        elif doc.source_type == "google_sheet":
            content = await fetch_google_sheet_content(doc.external_id or "")
        elif doc.source_type == "url":
            # Fetch and extract text from URL
            content = ""
        elif doc.source_type == "file":
            # Load from your storage and extract text
            content = ""
        else:
            raise ValueError(f"Unknown source_type: {doc.source_type}")

        doc.content = content
        doc.ingest_status = "succeeded"
        doc.ingest_error = None
    except Exception as e:
        doc.ingest_status = "failed"
        doc.ingest_error = str(e)
    finally:
        await session.commit()
