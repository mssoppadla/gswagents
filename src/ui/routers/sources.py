from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SecretRequest(BaseModel):
    org_id: int
    key: str
    value: str

class KnowledgeBaseRequest(BaseModel):
    org_id: int
    kb_name: str
    kb_url: str
    source_type: str  # "internal", "google_sheet", "google_doc"

class DeleteKBRequest(BaseModel):
    org_id: int
    kb_id: int

class GoogleSheetRequest(BaseModel):
    org_id: int
    sheet_url: str

class GoogleDocRequest(BaseModel):
    org_id: int
    doc_url: str

@router.post("/add-secret")
async def add_secret(payload: SecretRequest):
    return {"message": f"Secret {payload.key} added for org {payload.org_id}"}

@router.post("/add-knowledge-base")
async def add_kb(payload: KnowledgeBaseRequest):
    return {"message": f"Knowledge base {payload.kb_name} added for org {payload.org_id}"}

@router.post("/delete-knowledge-base")
async def delete_kb(payload: DeleteKBRequest):
    return {"message": f"Knowledge base {payload.kb_id} deleted for org {payload.org_id}"}

@router.post("/add-google-sheet")
async def add_google_sheet(payload: GoogleSheetRequest):
    return {"message": f"Google Sheet linked for org {payload.org_id}", "sheet_url": payload.sheet_url}

@router.post("/add-google-doc")
async def add_google_doc(payload: GoogleDocRequest):
    return {"message": f"Google Doc linked for org {payload.org_id}", "doc_url": payload.doc_url}
