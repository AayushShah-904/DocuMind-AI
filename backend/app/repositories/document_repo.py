from datetime import datetime, timezone
from typing import List, Optional

from beanie import PydanticObjectId

from app.core.logging import get_logger
from app.models.document import Document_, DocumentStatus, DocumentType

logger = get_logger(__name__)


class DocumentRepository:
    async def create(
        self,
        user_id: str,
        filename: str,
        original_filename: str,
        file_type: DocumentType,
        file_size_bytes: int,
    ) -> Document_:
        doc = Document_(
            user_id=PydanticObjectId(user_id),
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.PENDING,
        )
        await doc.insert()
        return doc

    async def get_by_id(self, doc_id: str) -> Optional[Document_]:
        return await Document_.get(PydanticObjectId(doc_id))

    async def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[Document_]:
        return (
            await Document_.find({"user_id": PydanticObjectId(user_id)})
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_by_user(self, user_id: str) -> int:
        return await Document_.find({"user_id": PydanticObjectId(user_id)}).count()

    async def update_status(
        self,
        doc_id: str,
        status: DocumentStatus,
        chunk_count: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        doc = await Document_.get(PydanticObjectId(doc_id))
        if doc:
            doc.status = status
            doc.chunk_count = chunk_count
            doc.error_message = error_message
            doc.updated_at = datetime.now(timezone.utc)
            await doc.save()

    async def delete(self, doc_id: str, user_id: str) -> bool:
        doc = await Document_.find_one(
            {"_id": PydanticObjectId(doc_id), "user_id": PydanticObjectId(user_id)}
        )
        if doc:
            await doc.delete()
            return True
        return False

    async def total_count(self) -> int:
        return await Document_.count()


document_repo = DocumentRepository()
