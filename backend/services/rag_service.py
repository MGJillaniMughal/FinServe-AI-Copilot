"""RAG orchestration: shared vector store + retrieval + grounded answers."""
import uuid
from datetime import datetime
from typing import Dict, List

from backend import database as db
from backend.services.vector_store import VectorStore, chunk_text
from backend.services.document_loader import extract_text
from backend.services.ai_engine import ai_engine
from backend.utils.logger import get_logger

logger = get_logger("rag-service")

# Single in-process retrieval index, rehydrated from the database on startup.
vector_store = VectorStore()


def rebuild_index() -> int:
    vector_store.reset()
    for ch in db.all_chunks():
        vector_store.add(ch["document_id"], ch["filename"], ch["text"])
    logger.info("Vector index rebuilt with %d chunks", len(vector_store.chunks))
    return len(vector_store.chunks)


def ingest(filename: str, category: str, raw: bytes) -> Dict:
    text, dtype = extract_text(filename, raw)
    pieces = chunk_text(text) if text.strip() else []
    doc_id = uuid.uuid4().hex[:12]
    summary = ai_engine.summarize(text) if text.strip() else ""
    doc = {
        "id": doc_id, "filename": filename, "category": category,
        "size_bytes": len(raw), "chunks": len(pieces), "summary": summary,
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    db.insert_document(doc, pieces)
    for p in pieces:
        vector_store.add(doc_id, filename, p)
    db.add_history({
        "id": uuid.uuid4().hex[:10], "type": "document",
        "title": f"Ingested {filename}",
        "summary": f"{len(pieces)} chunks indexed ({dtype}, {category}).",
        "score": None, "payload": {"summary": summary},
        "created_at": datetime.utcnow().isoformat(),
    })
    return doc


def query(question: str, top_k: int = 4) -> Dict:
    hits = vector_store.search(question, top_k)
    contexts = [c for _, c in hits]
    answer = ai_engine.answer(question, contexts, vector_store)
    citations = []
    for score, c in hits:
        snippet = c["text"][:220] + ("..." if len(c["text"]) > 220 else "")
        citations.append({"document_id": c["doc_id"], "filename": c["filename"],
                          "snippet": snippet, "score": score})
    top = hits[0][0] if hits else 0.0
    confidence = round(min(0.97, 0.45 + top * 0.6 + 0.04 * len(citations)), 2)
    db.add_history({
        "id": uuid.uuid4().hex[:10], "type": "rag",
        "title": f"Q&A: {question[:48]}",
        "summary": f"Answered from {len(citations)} source passage(s).",
        "score": None, "payload": {}, "created_at": datetime.utcnow().isoformat(),
    })
    return {"query": question, "answer": answer, "citations": citations,
            "confidence": confidence, "model": ai_engine.model, "mode": ai_engine.mode}
