"""System health & status."""
from datetime import datetime
from fastapi import APIRouter
from backend.config import settings
from backend.models import HealthResponse
from backend.services.ai_engine import ai_engine
from backend.services.rag_service import vector_store
from backend import database as db

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health():
    st = ai_engine.status()
    return HealthResponse(
        status="ok", app=settings.APP_NAME, vendor=settings.VENDOR, version=settings.VERSION,
        ai_mode=st["label"], ai_status=st["status"],
        documents_indexed=len(db.list_documents()),
        chunks_indexed=len(vector_store.chunks),
        timestamp=datetime.utcnow(),
    )
