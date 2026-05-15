from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.message import MessageRole


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None  # None = new session
    document_ids: Optional[List[str]] = None  # None = search all user docs

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the key findings of this report?",
                "session_id": None,
                "document_ids": None,
            }
        }


class SourceReference(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    excerpt: str
    score: float


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: MessageRole
    content: str
    sources: List[Dict[str, Any]]
    latency_ms: Optional[int]
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]
