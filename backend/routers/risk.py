"""AI risk advisor."""
from fastapi import APIRouter, Depends
from backend.models import RiskRequest, RiskResponse
from backend.services import risk_service
from backend.routers.deps import current_user

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/analyze", response_model=RiskResponse)
def analyze(payload: RiskRequest, user: dict = Depends(current_user)):
    return RiskResponse(**risk_service.analyze(payload.text, payload.subject or "Portfolio"))
