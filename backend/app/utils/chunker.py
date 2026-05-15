"""
Intelligent text chunking using LangChain's RecursiveCharacterTextSplitter.
Produces overlapping chunks with full metadata for traceability.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings


@dataclass
class TextChunk:
    index: int
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def chunk_text(
    text: str,
    filename: str,
    file_type: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[TextChunk]:
    """
    Split text into overlapping chunks with metadata.

    Returns a list of TextChunk objects, each with:
    - index: position in the document
    - content: the chunk text
    - metadata: filename, file_type, char_start, char_end
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"filename": filename, "file_type": file_type}],
    )

    chunks: List[TextChunk] = []
    char_position = 0

    for idx, doc in enumerate(raw_chunks):
        content = doc.page_content.strip()
        if not content:
            continue

        # Find the approximate character position in original text
        start = text.find(content[:50], char_position)
        if start == -1:
            start = char_position
        end = start + len(content)
        char_position = max(char_position, start)

        chunks.append(
            TextChunk(
                index=idx,
                content=content,
                metadata={
                    "filename": filename,
                    "file_type": file_type,
                    "char_start": start,
                    "char_end": end,
                    "chunk_index": idx,
                },
            )
        )

    return chunks
