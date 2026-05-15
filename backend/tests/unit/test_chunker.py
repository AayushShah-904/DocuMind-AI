"""Unit tests for the chunker utility."""

from app.utils.chunker import chunk_text


def test_chunk_text_basic():
    text = " ".join(["word"] * 600)
    chunks = chunk_text(text, "test.txt", "txt", chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.content.strip()
        assert "filename" in chunk.metadata


def test_chunk_text_empty_returns_empty():
    chunks = chunk_text("", "empty.txt", "txt")
    assert chunks == []


def test_chunk_metadata_has_required_keys():
    text = "This is a test document with enough text to create a chunk."
    chunks = chunk_text(text, "report.pdf", "pdf")
    assert len(chunks) >= 1
    meta = chunks[0].metadata
    assert "filename" in meta
    assert "file_type" in meta
    assert "chunk_index" in meta


def test_chunk_index_is_sequential():
    text = " ".join(["word"] * 1000)
    chunks = chunk_text(text, "doc.txt", "txt", chunk_size=100, chunk_overlap=10)
    indices = [c.index for c in chunks]
    assert indices == list(range(len(indices)))
