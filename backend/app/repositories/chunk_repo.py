from typing import Any, Dict, List

from beanie import PydanticObjectId

from app.core.logging import get_logger
from app.models.chunk import DocumentChunk

logger = get_logger(__name__)


class ChunkRepository:
    async def bulk_insert(self, chunks: List[DocumentChunk]) -> None:
        """Insert multiple chunks in one operation."""
        await DocumentChunk.insert_many(chunks)
        logger.info("Chunks inserted", count=len(chunks))

    async def get_by_document(self, document_id: str) -> List[DocumentChunk]:
        return (
            await DocumentChunk.find(
                DocumentChunk.document_id == PydanticObjectId(document_id)
            )
            .sort(DocumentChunk.chunk_index)
            .to_list()
        )

    async def delete_by_document(self, document_id: str) -> int:
        result = await DocumentChunk.find(
            DocumentChunk.document_id == PydanticObjectId(document_id)
        ).delete()
        return result.deleted_count if result else 0

    async def count_by_user(self, user_id: str) -> int:
        return await DocumentChunk.find(
            DocumentChunk.user_id == PydanticObjectId(user_id)
        ).count()

    async def total_count(self) -> int:
        return await DocumentChunk.count()

    async def get_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        oids = [PydanticObjectId(cid) for cid in chunk_ids]
        return await DocumentChunk.find(
            {"_id": {"$in": oids}}
        ).to_list()


chunk_repo = ChunkRepository()
