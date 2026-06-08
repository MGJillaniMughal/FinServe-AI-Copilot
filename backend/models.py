"""Typed Pydantic request/response schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ----- Auth -----
class LoginRequest(BaseModel):
    email: str = Field(..., examples=["admin@jillanisoftech.com"])
    password: str = Field(..., examples=["finserve123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    role: str
    expires_in: int


# ----- System -----
class HealthResponse(BaseModel):
    status: str
    app: str
    vendor: str
    version: str
    ai_mode: str
    ai_status: str
    documents_indexed: int
    chunks_indexed: int
    timestamp: datetime


# ----- Documents -----
class DocumentMeta(BaseModel):
    id: str
    filename: str
    category: str
    size_bytes: int
    chunks: int
    summary: Optional[str] = ""
    uploaded_at: datetime


class UploadResponse(BaseModel):
    document: DocumentMeta
    message: str


# ----- RAG -----
class RAGQuery(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(4, ge=1, le=10)


class Citation(BaseModel):
    document_id: str
    filename: str
    snippet: str
    score: float


class RAGResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    confidence: float
    model: str
    mode: str


# ----- Risk -----
class RiskRequest(BaseModel):
    text: str = Field(..., min_length=1)
    subject: Optional[str] = "Portfolio"


class RiskResponse(BaseModel):
    subject: str
    risk_score: float
    risk_category: str
    key_findings: List[str]
    risk_drivers: List[str]
    mitigation: List[str]
    confidence: float
    model: str


# ----- Compliance -----
class ComplianceRequest(BaseModel):
    text: str = Field(..., min_length=1)
    framework: Optional[str] = "ALL"


class FrameworkScore(BaseModel):
    name: str
    coverage: float
    status: str


class ComplianceResponse(BaseModel):
    compliance_score: float
    risk_level: str
    frameworks: List[FrameworkScore]
    findings: List[str]
    recommendations: List[str]
    human_review: bool
    model: str


# ----- History -----
class HistoryItem(BaseModel):
    id: str
    type: str
    title: str
    summary: str
    score: Optional[float] = None
    created_at: datetime
