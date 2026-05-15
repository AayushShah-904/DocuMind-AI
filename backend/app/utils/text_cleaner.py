"""
Text cleaning utilities.
Normalizes whitespace and removes artifacts from parsed documents.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline: normalize unicode → remove control chars →
    collapse whitespace → strip.
    """
    text = _normalize_unicode(text)
    text = _remove_control_characters(text)
    text = _fix_whitespace(text)
    text = text.strip()
    return text


def _normalize_unicode(text: str) -> str:
    """Normalize to NFC form and replace smart quotes with ASCII equivalents."""
    text = unicodedata.normalize("NFC", text)
    # Smart quotes → standard
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "--")
    text = text.replace("\u2026", "...")
    return text


def _remove_control_characters(text: str) -> str:
    """Remove non-printable control characters except newline and tab."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def _fix_whitespace(text: str) -> str:
    """Collapse multiple blank lines to max two, normalize spaces."""
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    # Collapse multiple spaces (but not newlines)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text
