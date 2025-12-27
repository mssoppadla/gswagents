from fastapi import APIRouter

router = APIRouter()

@router.post("/add-knowledge-base")
async def add_kb(org_id: int, kb_name: str, kb_url: str):
    # TODO: attach KB to org
    return {"message": f"Knowledge base {kb_name} added for org {org_id}"}

@router.delete("/delete-knowledge-base/{kb_id}")
async def delete_kb(org_id: int, kb_id: int):
    # TODO: remove KB from org
    return {"message": f"Knowledge base {kb_id} deleted for org {org_id}"}

@router.post("/add-google-sheet")
async def add_google_sheet(org_id: int, sheet_url: str):
    # TODO: link Google Sheet as KB source
    return {"message": f"Google Sheet linked for org {org_id}", "sheet_url": sheet_url}

@router.post("/add-google-doc")
async def add_google_doc(org_id: int, doc_url: str):
    # TODO: link Google Doc as KB source
    return {"message": f"Google Doc linked for org {org_id}", "doc_url": doc_url}
