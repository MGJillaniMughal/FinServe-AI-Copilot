"""Seed the database with a demo admin user and realistic sample corpus.

Runs once on first startup so dashboards are populated for demos.
Developed by Jillani SofTech.
"""
import uuid
from datetime import datetime, timedelta

from backend.config import settings
from backend import database as db
from backend.security import hash_password
from backend.services.rag_service import ingest, rebuild_index
from backend.utils.logger import get_logger

logger = get_logger("seed")

SAMPLE_DOCS = [
    ("Q1_Risk_Report.txt", "Risk Reports",
     b"The portfolio shows elevated concentration risk and rising volatility this quarter. "
     b"Counterparty exposure increased due to higher leverage in the credit book. Liquidity "
     b"remains adequate but covenant headroom is tight and a downgrade is possible. We recommend "
     b"diversification, position limits and quarterly stress tests to reduce default probability."),
    ("AML_Policy_2025.txt", "AML/KYC",
     b"This Anti-Money Laundering policy defines suspicious activity monitoring, SAR filing and "
     b"FATF-aligned screening controls. Know Your Customer onboarding requires identity verification "
     b"and customer due diligence. Enhanced due diligence applies to politically exposed and high-risk customers."),
    ("KYC_Onboarding.txt", "AML/KYC",
     b"Know Your Customer onboarding covers identity verification, document checks and ongoing "
     b"monitoring. Risk-based customer due diligence is refreshed annually for high-risk segments."),
    ("Audit_Report_FY24.txt", "Audit",
     b"Internal audit reviewed access control and the audit trail. SOC 2 trust services criteria "
     b"for availability and security were largely met, with minor change-management exceptions."),
    ("Investment_Research.txt", "Research",
     b"Equity research indicates stable diversified earnings with hedged currency exposure. "
     b"Downside scenarios reflect modest volatility and a healthy capital surplus."),
    ("GDPR_Data_Notice.txt", "Compliance",
     b"This notice describes personal data processing, data subject rights, consent and the right "
     b"to erasure under GDPR. Data retention schedules are documented."),
]


def seed() -> None:
    db.init_db()
    # demo user
    if not db.get_user(settings.DEMO_EMAIL):
        db.create_user(settings.DEMO_EMAIL, settings.DEMO_NAME, hash_password(settings.DEMO_PASSWORD))
        logger.info("Created demo user: %s", settings.DEMO_EMAIL)

    if db.list_documents():
        rebuild_index()
        return

    for name, cat, raw in SAMPLE_DOCS:
        ingest(name, cat, raw)
    logger.info("Seeded %d sample documents", len(SAMPLE_DOCS))
