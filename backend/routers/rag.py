"""RAG question answering."""
from fastapi import APIRouter, Depends
from backend.models import RAGQuery, RAGResponse
from backend.services import rag_service
from backend.routers.deps import current_user

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RAGResponse)
def query(payload: RAGQuery, user: dict = Depends(current_user)):
    return RAGResponse(**rag_service.query(payload.query, payload.top_k))
