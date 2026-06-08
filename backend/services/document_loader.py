"""Document text extraction for PDF, DOCX, TXT and Markdown.

Heavy parsers (pypdf, python-docx) are optional: when they are not
installed the loader degrades gracefully and still ingests text files.

Developed by Jillani SofTech.
"""
import io
from typing import Tuple

from backend.utils.logger import get_logger

logger = get_logger("doc-loader")


def extract_text(filename: str, raw: bytes) -> Tuple[str, str]:
    """Return (text, detected_type)."""
    name = (filename or "").lower()

    if name.endswith(".pdf"):
        return _pdf(raw), "pdf"
    if name.endswith(".docx"):
        return _docx(raw), "docx"
    # txt / md / csv / fallback
    return raw.decode("utf-8", errors="ignore"), "text"


def _pdf(raw: bytes) -> str:
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        logger.warning("PDF parse unavailable (%s). Install 'pypdf' for PDF support.", exc)
        return ""


def _docx(raw: bytes) -> str:
    try:
        import docx  # python-docx
        document = docx.Document(io.BytesIO(raw))
        return "\n".join(p.text for p in document.paragraphs)
    except Exception as exc:
        logger.warning("DOCX parse unavailable (%s). Install 'python-docx' for DOCX support.", exc)
        return ""
