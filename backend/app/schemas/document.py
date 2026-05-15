from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size_bytes: int
    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentStatusResponse(BaseModel):
    id: str
    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str]
