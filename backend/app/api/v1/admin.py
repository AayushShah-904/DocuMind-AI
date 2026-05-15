from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_admin_user
from app.models.user import User
from app.repositories.chat_repo import chat_repo
from app.repositories.chunk_repo import chunk_repo
from app.repositories.document_repo import document_repo
from app.repositories.user_repo import user_repo

router = APIRouter(prefix="/admin", tags=["Admin"])


class AdminStats(BaseModel):
    total_users: int
    total_documents: int
    total_chunks: int
    total_messages: int


@router.get("/overview", response_model=AdminStats)
async def admin_overview(_: User = Depends(get_admin_user)):
    """System-wide analytics. Admin access only."""
    return AdminStats(
        total_users=await user_repo.count(),
        total_documents=await document_repo.total_count(),
        total_chunks=await chunk_repo.total_count(),
        total_messages=await chat_repo.total_message_count(),
    )
