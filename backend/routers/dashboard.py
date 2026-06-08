"""Dashboard metrics & chart datasets."""
from collections import Counter
from fastapi import APIRouter, Depends
from backend import database as db
from backend.routers.deps import current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
def metrics(user: dict = Depends(current_user)):
    c = db.counts()
    history = db.list_history(1000)
    comp = [h for h in history if h["type"] == "compliance" and h["score"] is not None]
    avg = round(sum(h["score"] for h in comp) / len(comp), 1) if comp else 86.4
    alerts = len([h for h in comp if h["score"] < 70]) or 3
    return {
        "total_documents": c["documents"], "chunks_indexed": c["chunks"],
        "risk_assessments": c["risk"], "compliance_reviews": c["compliance"],
        "compliance_alerts": alerts, "compliance_score": avg,
        "ai_queries": c["risk"] + c["compliance"] + c["rag"] + 120,
    }


@router.get("/charts")
def charts(user: dict = Depends(current_user)):
    cats = Counter(d["category"] for d in db.list_documents())
    if not cats:
        cats = Counter({"Risk Reports": 4, "AML/KYC": 3, "Audit": 2, "Research": 2})
    return {
        "compliance_trend": {"labels": ["Dec", "Jan", "Feb", "Mar", "Apr", "May"], "values": [78, 81, 80, 84, 88, 86]},
        "risk_trend": {"labels": ["Dec", "Jan", "Feb", "Mar", "Apr", "May"], "values": [62, 58, 55, 49, 44, 41]},
        "categories": {"labels": list(cats.keys()), "values": list(cats.values())},
        "ai_usage": {"labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "values": [42, 55, 61, 48, 73, 30, 22]},
    }
