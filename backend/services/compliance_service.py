"""Compliance service: framework review + history persistence."""
import uuid
from datetime import datetime

from backend import database as db
from backend.services.ai_engine import ai_engine


def review(text: str, framework: str) -> dict:
    result = ai_engine.review_compliance(text, framework)
    db.add_history({
        "id": uuid.uuid4().hex[:10], "type": "compliance",
        "title": "Compliance review",
        "summary": f"{result['risk_level']} risk (score {result['compliance_score']}).",
        "score": result["compliance_score"], "payload": result,
        "created_at": datetime.utcnow().isoformat(),
    })
    return result
