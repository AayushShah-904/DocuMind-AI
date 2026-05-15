"""
Document service: validates upload, parses, chunks, generates embeddings,
and stores everything in MongoDB. Processing runs as a FastAPI background task.
"""

import uuid

from fastapi import BackgroundTasks, UploadFile

from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    ProcessingError,
    UnsupportedFileTypeError,
)
from app.core.logging import get_logger
from app.models.chunk import DocumentChunk
from app.models.document import Document_, DocumentStatus, DocumentType
from app.repositories.chunk_repo import chunk_repo
from app.repositories.document_repo import document_repo
from app.services.embedding_service import embed_texts
from app.utils.chunker import chunk_text
from app.utils.file_parser import parse_file
from app.utils.text_cleaner import clean_text

logger = get_logger(__name__)


class DocumentService:
    async def upload(
        self,
        file: UploadFile,
        user_id: str,
        background_tasks: BackgroundTasks,
    ) -> Document_:
        """
        Validate, persist metadata, then kick off background processing.
        Returns immediately with status=pending so the user isn't waiting.
        """
        content = await file.read()
        self._validate_file(file.filename or "", len(content))

        ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        doc = await document_repo.create(
            user_id=user_id,
            filename=f"{uuid.uuid4().hex}.{ext}",
            original_filename=file.filename or "unknown",
            file_type=DocumentType(ext),
            file_size_bytes=len(content),
        )

        background_tasks.add_task(
            self._process_document,
            doc_id=str(doc.id),
            content=content,
            filename=file.filename or "unknown",
            file_type=ext,
        )
        logger.info("Document queued for processing", doc_id=str(doc.id))
        return doc

    def _validate_file(self, filename: str, size_bytes: int) -> None:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in settings.allowed_extensions_list:
            raise UnsupportedFileTypeError(ext, settings.allowed_extensions_list)
        if size_bytes > settings.max_upload_size_bytes:
            raise FileTooLargeError(settings.MAX_UPLOAD_SIZE_MB)

    async def _process_document(
        self, doc_id: str, content: bytes, filename: str, file_type: str
    ) -> None:
        """Background task: parse → clean → chunk → embed → store."""
        import asyncio

        try:
            await document_repo.update_status(doc_id, DocumentStatus.PROCESSING)

            def _cpu_bound_processing():
                # 1. Parse
                raw_text = parse_file(content, filename)
                if not raw_text.strip():
                    raise ProcessingError("Document appears to be empty or unreadable.")

                # 2. Clean
                clean = clean_text(raw_text)

                # 3. Chunk
                text_chunks = chunk_text(clean, filename, file_type)
                if not text_chunks:
                    raise ProcessingError("No text chunks could be generated.")

                # 4. Embed
                texts = [c.content for c in text_chunks]
                embeddings = embed_texts(texts)
                return text_chunks, embeddings

            text_chunks, embeddings = await asyncio.to_thread(_cpu_bound_processing)

            # 5. Build Beanie documents
            from beanie import PydanticObjectId

            doc = await document_repo.get_by_id(doc_id)
            user_id = doc.user_id

            chunk_docs = [
                DocumentChunk(
                    document_id=PydanticObjectId(doc_id),
                    user_id=user_id,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    embedding=embeddings[i],
                    metadata=chunk.metadata,
                )
                for i, chunk in enumerate(text_chunks)
            ]

            # 6. Store
            await chunk_repo.bulk_insert(chunk_docs)

            # 7. Mark ready
            await document_repo.update_status(
                doc_id, DocumentStatus.READY, chunk_count=len(chunk_docs)
            )
            logger.info(
                "Document processed",
                doc_id=doc_id,
                chunks=len(chunk_docs),
            )

        except Exception as e:
            logger.error("Document processing failed", doc_id=doc_id, error=str(e))
            await document_repo.update_status(
                doc_id,
                DocumentStatus.FAILED,
                error_message=str(e),
            )

    async def delete(self, doc_id: str, user_id: str) -> bool:
        deleted = await document_repo.delete(doc_id, user_id)
        if deleted:
            await chunk_repo.delete_by_document(doc_id)
            logger.info("Document deleted", doc_id=doc_id)
        return deleted


document_service = DocumentService()
