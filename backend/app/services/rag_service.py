"""
RAG service: full pipeline from question to streamed answer.
Uses LangChain + Gemini 2.5 Flash for generation.
"""

import time
from typing import AsyncGenerator, List, Optional

from langchain.schema import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import get_logger
from app.models.message import MessageRole
from app.repositories.chat_repo import chat_repo
from app.services.retrieval_service import retrieval_service

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are DocuMind, an AI assistant that answers questions \
based on the user's uploaded documents.

Your job:
- Answer questions using ONLY the provided document context below
- Be precise, factual, and grounded in the sources given
- If the answer isn't in the context, say so clearly — don't make things up
- Cite document chunks by filename when relevant (e.g., "According to report.pdf...")
- Format answers clearly using markdown when helpful (lists, bold, headers)

Context from documents:
{context}"""


def _build_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GEMINI_API_KEY,
        streaming=True,
        temperature=0.3,
        convert_system_message_to_human=True,
    )


class RAGService:
    def __init__(self):
        self._llm: Optional[ChatGoogleGenerativeAI] = None

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm is None:
            self._llm = _build_llm()
        return self._llm

    async def ask(
        self,
        question: str,
        user_id: str,
        session_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Full RAG pipeline. Yields SSE-formatted strings.
        Final event contains sources JSON.
        """
        start_ms = int(time.time() * 1000)

        # ── 1. Get or create session ──────────────────────────────────────────
        if not session_id:
            session = await chat_repo.create_session(
                user_id=user_id,
                title=question[:60] + ("..." if len(question) > 60 else ""),
                document_ids=document_ids,
            )
            session_id = str(session.id)
        else:
            session = await chat_repo.get_session(session_id, user_id)
            if not session:
                session = await chat_repo.create_session(user_id=user_id)
                session_id = str(session.id)

        # ── 2. Persist user message ───────────────────────────────────────────
        await chat_repo.add_message(
            session_id=session_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=question,
        )

        # ── 3. Retrieve context ───────────────────────────────────────────────
        chunks = await retrieval_service.retrieve(
            query=question,
            user_id=user_id,
            document_ids=document_ids,
        )

        # ── 4. Build context string ───────────────────────────────────────────
        context_parts = []
        for i, chunk in enumerate(chunks):
            fname = chunk["metadata"].get("filename", "document")
            context_parts.append(
                f"[Source {i+1} — {fname}, chunk {chunk['chunk_index']}]\n"
                f"{chunk['content']}"
            )
        context = (
            "\n\n---\n\n".join(context_parts)
            if context_parts
            else "No relevant documents found."
        )

        # ── 5. Build conversation history ─────────────────────────────────────
        history = await chat_repo.get_messages(session_id, limit=10)
        history_messages = []
        for msg in history[:-1]:  # exclude the message we just added
            if msg.role == MessageRole.USER:
                history_messages.append(HumanMessage(content=msg.content))

        # ── 6. Stream response ────────────────────────────────────────────────
        system_msg = SYSTEM_PROMPT.format(context=context)
        messages = [
            SystemMessage(content=system_msg),
            *history_messages,
            HumanMessage(content=question),
        ]

        full_response = ""
        yield f'data: {{"session_id": "{session_id}", "type": "start"}}\n\n'

        try:
            async for chunk_msg in self.llm.astream(messages):
                token = chunk_msg.content
                if token:
                    full_response += token
                    safe = token.replace('"', '\\"').replace("\n", "\\n")
                    yield f'data: {{"type": "token", "content": "{safe}"}}\n\n'
        except Exception as e:
            logger.error("LLM streaming failed", error=str(e))
            yield (
                f'data: {{"type": "error", "content": '
                f'"Generation failed: {str(e)[:100]}"}}\n\n'
            )
            return

        # ── 7. Persist assistant message ──────────────────────────────────────
        latency_ms = int(time.time() * 1000) - start_ms
        sources = [
            {
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "filename": c["metadata"].get("filename", ""),
                "chunk_index": c["chunk_index"],
                "excerpt": c["content"][:200],
                "score": round(c["score"], 4),
            }
            for c in chunks
        ]

        await chat_repo.add_message(
            session_id=session_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=full_response,
            sources=sources,
            latency_ms=latency_ms,
        )

        # Update session message count
        await chat_repo.update_session(
            session_id,
            message_count=session.message_count + 2,
        )

        import json

        yield (
            f'data: {{"type": "done", "sources": {json.dumps(sources)}, '
            f'"session_id": "{session_id}", "latency_ms": {latency_ms}}}\n\n'
        )


rag_service = RAGService()
