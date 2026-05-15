"""
File parser utilities for PDF, DOCX, and TXT documents.
Returns extracted plain text ready for chunking.
"""

import io
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_file(content: bytes, filename: str) -> str:
    """
    Parse uploaded file bytes into a plain text string.

    Supports: .pdf, .docx, .txt
    Raises ValueError for unsupported types.
    """
    suffix = Path(filename).suffix.lower().lstrip(".")

    if suffix == "pdf":
        return _parse_pdf(content)
    elif suffix == "docx":
        return _parse_docx(content)
    elif suffix == "txt":
        return _parse_txt(content)
    else:
        raise ValueError(f"Unsupported file type: .{suffix}")


def _parse_pdf(content: bytes) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        pages = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {page_num + 1}]\n{text}")
        return "\n\n".join(pages)
    except Exception as e:
        logger.error("PDF parsing failed", error=str(e))
        raise ValueError(f"Could not parse PDF: {e}") from e


def _parse_docx(content: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document as DocxDocument

        doc = DocxDocument(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.error("DOCX parsing failed", error=str(e))
        raise ValueError(f"Could not parse DOCX: {e}") from e


def _parse_txt(content: bytes) -> str:
    """Decode TXT file, trying common encodings."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file with any supported encoding.")
