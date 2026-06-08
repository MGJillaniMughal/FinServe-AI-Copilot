"""Compliance intelligence engine."""
from fastapi import APIRouter, Depends
from backend.models import ComplianceRequest, ComplianceResponse
from backend.services import compliance_service
from backend.routers.deps import current_user

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/review", response_model=ComplianceResponse)
def review(payload: ComplianceRequest, user: dict = Depends(current_user)):
    return ComplianceResponse(**compliance_service.review(payload.text, payload.framework or "ALL"))
