# FinServe AI Copilot - Architecture
*Engineered by Jillani SofTech (Muhammad Ghulam Jillani)*

## Layers

```
Frontend (HTML5 / CSS3 / Vanilla JS / Bootstrap 5 / Chart.js)
   |  JWT bearer token  |  REST / JSON
   v
FastAPI Application (backend/main.py)
   |
   +-- Auth (JWT HS256, PBKDF2 password hashing - stdlib)
   +-- Routers: auth, health, documents, rag, risk, compliance, analysis, dashboard
   +-- Service layer
   |     |-- vector_store        TF-IDF + cosine retrieval (embeddings-ready)
   |     |-- document_loader     PDF / DOCX / TXT extraction
   |     |-- ai_engine           LLM mode (OpenAI) or Local Intelligence mode
   |     |-- rag_service / risk_service / compliance_service
   +-- Persistence: SQLite (documents, chunks, history, users)
```

## RAG pipeline
1. Upload -> text extraction (PDF/DOCX/TXT)
2. Chunking (word window with overlap)
3. Vectorisation (TF-IDF; OpenAI embeddings when configured)
4. Cosine similarity search (top-k)
5. Context retrieval + sentence ranking
6. Grounded answer generation (LLM or Local Intelligence)
7. Citation tracking (filename + relevance score)

## AI modes
- **LLM** - active when `OPENAI_API_KEY` is set and `openai` is installed.
- **Local Intelligence** - deterministic weighted-lexicon + TF-IDF engine, fully offline.

The active mode is reported at `GET /health` (`ai_mode`, `ai_status`).

## Security
- Stateless JWT (HS256) signed with `SECRET_KEY`, 12-hour expiry by default.
- Passwords stored as PBKDF2-HMAC-SHA256 with per-user salt.
- All data endpoints require a valid bearer token.
