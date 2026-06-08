"""Central application configuration (12-factor, environment driven).

Developed by Jillani SofTech (Muhammad Ghulam Jillani).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    # --- Product identity ---
    APP_NAME: str = "FinServe AI Copilot"
    VENDOR: str = "Jillani SofTech"
    AUTHOR: str = "Muhammad Ghulam Jillani"
    VERSION: str = "2.0.0"

    # --- LLM / AI ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # --- Security / Auth ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jillani-softech-finserve-dev-secret-change-me")
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "720"))
    DEMO_EMAIL: str = os.getenv("DEMO_EMAIL", "admin@jillanisoftech.com")
    DEMO_PASSWORD: str = os.getenv("DEMO_PASSWORD", "finserve123")
    DEMO_NAME: str = os.getenv("DEMO_NAME", "Jillani SofTech Admin")

    # --- Persistence ---
    DB_PATH: str = os.getenv("DB_PATH", str(BASE_DIR / "finserve.db"))

    # --- Server ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
