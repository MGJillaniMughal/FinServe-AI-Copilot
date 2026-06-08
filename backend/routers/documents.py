"""Document ingestion & listing."""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from backend.models import UploadResponse, DocumentMeta
from backend.services import rag_service
from backend import database as db
from backend.routers.deps import current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...), category: str = Form("General"),
                 user: dict = Depends(current_user)):
    raw = await file.read()
    doc = rag_service.ingest(file.filename, category, raw)
    return UploadResponse(document=DocumentMeta(**doc),
                          message=f"Document ingested and indexed into {doc['chunks']} chunks.")


@router.get("", response_model=list[DocumentMeta])
def list_documents(user: dict = Depends(current_user)):
    return [DocumentMeta(**d) for d in db.list_documents()]
