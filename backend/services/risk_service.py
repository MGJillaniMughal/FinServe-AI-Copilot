"""Risk service: scoring + history persistence."""
import uuid
from datetime import datetime

from backend import database as db
from backend.services.ai_engine import ai_engine


def analyze(text: str, subject: str) -> dict:
    result = ai_engine.analyze_risk(text, subject)
    db.add_history({
        "id": uuid.uuid4().hex[:10], "type": "risk",
        "title": f"Risk analysis: {subject}",
        "summary": f"{result['risk_category']} risk (score {result['risk_score']}).",
        "score": result["risk_score"], "payload": result,
        "created_at": datetime.utcnow().isoformat(),
    })
    return result
