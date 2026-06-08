"""SQLite persistence layer (documents, chunks, history, users).

Uses the standard-library sqlite3 driver so the platform persists data
across restarts with no external database to install.

Developed by Jillani SofTech.
"""
import json
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("database")
_lock = threading.Lock()


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock, _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                role TEXT DEFAULT 'admin',
                password_hash TEXT NOT NULL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                category TEXT,
                size_bytes INTEGER,
                chunks INTEGER,
                summary TEXT,
                uploaded_at TEXT
            );
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT,
                filename TEXT,
                ordinal INTEGER,
                text TEXT
            );
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                summary TEXT,
                score REAL,
                payload TEXT,
                created_at TEXT
            );
            """
        )
    logger.info("Database initialised at %s", settings.DB_PATH)


# ----- Users -----
def get_user(email: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def create_user(email: str, name: str, password_hash: str, role: str = "admin") -> None:
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO users (email, name, role, password_hash, created_at) VALUES (?,?,?,?,?)",
            (email, name, role, password_hash, datetime.utcnow().isoformat()),
        )


# ----- Documents & chunks -----
def insert_document(doc: Dict[str, Any], chunk_texts: List[str]) -> None:
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO documents (id, filename, category, size_bytes, chunks, summary, uploaded_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (doc["id"], doc["filename"], doc["category"], doc["size_bytes"],
             doc["chunks"], doc.get("summary", ""), doc["uploaded_at"]),
        )
        for i, t in enumerate(chunk_texts):
            c.execute(
                "INSERT INTO chunks (document_id, filename, ordinal, text) VALUES (?,?,?,?)",
                (doc["id"], doc["filename"], i, t),
            )


def list_documents() -> List[Dict[str, Any]]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")]


def all_chunks() -> List[Dict[str, Any]]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT document_id, filename, text FROM chunks")]


def count_chunks() -> int:
    with _conn() as c:
        return c.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()["n"]


# ----- History -----
def add_history(item: Dict[str, Any]) -> None:
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO history (id, type, title, summary, score, payload, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (item["id"], item["type"], item["title"], item["summary"],
             item.get("score"), json.dumps(item.get("payload", {})), item["created_at"]),
        )


def list_history(limit: int = 50) -> List[Dict[str, Any]]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["payload"] = json.loads(d.get("payload") or "{}")
            out.append(d)
        return out


def counts() -> Dict[str, int]:
    with _conn() as c:
        def n(q):
            return c.execute(q).fetchone()[0]
        return {
            "documents": n("SELECT COUNT(*) FROM documents"),
            "chunks": n("SELECT COUNT(*) FROM chunks"),
            "risk": n("SELECT COUNT(*) FROM history WHERE type='risk'"),
            "compliance": n("SELECT COUNT(*) FROM history WHERE type='compliance'"),
            "rag": n("SELECT COUNT(*) FROM history WHERE type='rag'"),
        }
