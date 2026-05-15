from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import check_rate_limit, get_current_user
from app.core.exceptions import http_400, http_404
from app.models.user import User
from app.repositories.chat_repo import chat_repo
from app.schemas.chat import (
    AskRequest,
    MessageResponse,
    SessionDetailResponse,
    SessionResponse,
)
from app.services.rag_service import rag_service

router = APIRouter(prefix="/conversations", tags=["Chat"])


def _fmt_session(s) -> SessionResponse:
    return SessionResponse(
        id=str(s.id),
        title=s.title,
        message_count=s.message_count,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _fmt_message(m) -> MessageResponse:
    return MessageResponse(
        id=str(m.id),
        session_id=str(m.session_id),
        role=m.role,
        content=m.content,
        sources=m.sources,
        latency_ms=m.latency_ms,
        created_at=m.created_at,
    )


@router.post("/ask")
async def ask(
    body: AskRequest,
    current_user: User = Depends(check_rate_limit),
):
    """
    Ask a question against your uploaded documents.
    Returns a Server-Sent Events stream of tokens followed by a final sources event.
    """
    try:
        stream = rag_service.ask(
            question=body.question,
            user_id=str(current_user.id),
            session_id=body.session_id,
            document_ids=body.document_ids,
        )
        return StreamingResponse(
            stream,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise http_400(str(e))


@router.get("", response_model=List[SessionResponse])
async def list_conversations(current_user: User = Depends(get_current_user)):
    """List all chat sessions for the current user."""
    sessions = await chat_repo.list_sessions(str(current_user.id))
    return [_fmt_session(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve full message history for a session."""
    session = await chat_repo.get_session(session_id, str(current_user.id))
    if not session:
        raise http_404("Conversation not found.")
    messages = await chat_repo.get_messages(session_id, limit=100)
    return SessionDetailResponse(
        session=_fmt_session(session),
        messages=[_fmt_message(m) for m in messages],
    )


@router.delete("/{session_id}", status_code=204)
async def delete_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a conversation and all its messages."""
    deleted = await chat_repo.delete_session(session_id, str(current_user.id))
    if not deleted:
        raise http_404("Conversation not found.")
