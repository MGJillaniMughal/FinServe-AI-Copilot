"""Analysis history."""
from fastapi import APIRouter, Depends
from backend.models import HistoryItem
from backend import database as db
from backend.routers.deps import current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = 50, user: dict = Depends(current_user)):
    return [HistoryItem(**h) for h in db.list_history(limit)]
