from datetime import datetime, timezone
from typing import List, Optional

from beanie import PydanticObjectId

from app.core.logging import get_logger
from app.models.chat_session import ChatSession
from app.models.message import Message, MessageRole

logger = get_logger(__name__)


class ChatRepository:
    # ── Sessions ─────────────────────────────────────────────────────────────

    async def create_session(
        self,
        user_id: str,
        title: str = "New Conversation",
        document_ids: Optional[List[str]] = None,
    ) -> ChatSession:
        session = ChatSession(
            user_id=PydanticObjectId(user_id),
            title=title,
            document_ids=[PydanticObjectId(d) for d in (document_ids or [])],
        )
        await session.insert()
        return session

    async def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        return await ChatSession.find_one(
            ChatSession.id == PydanticObjectId(session_id),
            ChatSession.user_id == PydanticObjectId(user_id),
        )

    async def list_sessions(self, user_id: str) -> List[ChatSession]:
        return (
            await ChatSession.find(ChatSession.user_id == PydanticObjectId(user_id))
            .sort(-ChatSession.updated_at)
            .to_list()
        )

    async def update_session(self, session_id: str, **kwargs) -> None:
        session = await ChatSession.get(PydanticObjectId(session_id))
        if session:
            for k, v in kwargs.items():
                setattr(session, k, v)
            session.updated_at = datetime.now(timezone.utc)
            await session.save()

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        session = await ChatSession.find_one(
            ChatSession.id == PydanticObjectId(session_id),
            ChatSession.user_id == PydanticObjectId(user_id),
        )
        if session:
            # Also delete all messages in this session
            await Message.find(
                Message.session_id == PydanticObjectId(session_id)
            ).delete()
            await session.delete()
            return True
        return False

    # ── Messages ──────────────────────────────────────────────────────────────

    async def add_message(
        self,
        session_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        sources: Optional[list] = None,
        latency_ms: Optional[int] = None,
    ) -> Message:
        msg = Message(
            session_id=PydanticObjectId(session_id),
            user_id=PydanticObjectId(user_id),
            role=role,
            content=content,
            sources=sources or [],
            latency_ms=latency_ms,
        )
        await msg.insert()
        return msg

    async def get_messages(self, session_id: str, limit: int = 20) -> List[Message]:
        return (
            await Message.find(Message.session_id == PydanticObjectId(session_id))
            .sort(Message.created_at)
            .limit(limit)
            .to_list()
        )

    async def total_message_count(self) -> int:
        return await Message.count()


chat_repo = ChatRepository()
