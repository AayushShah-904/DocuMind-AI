"""
Hybrid retrieval service combining:
1. Semantic search via MongoDB Atlas Vector Search
2. Keyword search via brute-force text matching (fallback when Atlas Search unavailable)
3. Reciprocal Rank Fusion (RRF) to merge both result lists
4. Cross-encoder reranking for precision boost
"""

from typing import Any, Dict, List, Optional

from beanie import PydanticObjectId

from app.core.config import settings
from app.core.logging import get_logger
from app.db.mongodb import get_db_client
from app.models.chunk import DocumentChunk
from app.services.embedding_service import embed_query

logger = get_logger(__name__)

RRF_K = 60  # standard RRF constant


class RetrievalService:
    async def retrieve(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Full hybrid retrieval pipeline.
        Returns list of dicts: {chunk, score}
        """
        k = top_k or settings.TOP_K

        # 1. Semantic search
        semantic_results = await self._semantic_search(
            query, user_id, document_ids, k * 3
        )

        # 2. Keyword search
        keyword_results = await self._keyword_search(
            query, user_id, document_ids, k * 3
        )

        # 3. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(semantic_results, keyword_results)

        # 4. Rerank top candidates
        candidates = fused[: k * 2]
        reranked = await self._rerank(query, candidates)

        return reranked[:k]

    async def _semantic_search(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Atlas Vector Search or numpy cosine fallback."""
        query_vector = embed_query(query)

        try:
            return await self._atlas_vector_search(
                query_vector, user_id, document_ids, limit
            )
        except Exception as e:
            logger.warning(
                "Atlas Vector Search failed, using numpy fallback", error=str(e)
            )
            return await self._numpy_cosine_search(
                query_vector, user_id, document_ids, limit
            )

    async def _atlas_vector_search(
        self,
        query_vector: List[float],
        user_id: str,
        document_ids: Optional[List[str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        client = get_db_client()
        db = client[settings.MONGODB_DB_NAME]
        collection = db["chunks"]

        pre_filter: Dict[str, Any] = {"user_id": PydanticObjectId(user_id)}
        if document_ids:
            pre_filter["document_id"] = {
                "$in": [PydanticObjectId(d) for d in document_ids]
            }

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "filter": pre_filter,
                }
            },
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "document_id": 1,
                    "chunk_index": 1,
                    "score": 1,
                }
            },
        ]

        results = []
        async for doc in collection.aggregate(pipeline):
            results.append(
                {
                    "chunk_id": str(doc["_id"]),
                    "document_id": str(doc["document_id"]),
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "chunk_index": doc.get("chunk_index", 0),
                    "score": doc.get("score", 0.0),
                    "search_type": "semantic",
                }
            )
        return results

    async def _numpy_cosine_search(
        self,
        query_vector: List[float],
        user_id: str,
        document_ids: Optional[List[str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """In-memory cosine similarity fallback (for local dev without Atlas index)."""
        import numpy as np

        filters = [DocumentChunk.user_id == PydanticObjectId(user_id)]
        if document_ids:
            filters.append(
                {"document_id": {"$in": [PydanticObjectId(d) for d in document_ids]}}
            )

        chunks = await DocumentChunk.find(*filters).to_list()
        if not chunks:
            return []

        q = np.array(query_vector, dtype=np.float32)
        scored = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            v = np.array(chunk.embedding, dtype=np.float32)
            score = float(np.dot(q, v))  # already normalized → cosine similarity
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, chunk in scored[:limit]:
            results.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "chunk_index": chunk.chunk_index,
                    "score": score,
                    "search_type": "semantic_fallback",
                }
            )
        return results

    async def _keyword_search(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Simple keyword matching fallback (Atlas Search optional)."""
        # Split query into keywords
        keywords = [w.lower().strip() for w in query.split() if len(w) > 2]
        if not keywords:
            return []

        filters: Dict[str, Any] = {"user_id": PydanticObjectId(user_id)}
        if document_ids:
            filters["document_id"] = {
                "$in": [PydanticObjectId(d) for d in document_ids]
            }

        client = get_db_client()
        db = client[settings.MONGODB_DB_NAME]
        collection = db["chunks"]

        # Use $text search if available, else regex
        try:
            text_filter = {**filters, "$text": {"$search": query}}
            cursor = (
                collection.find(
                    text_filter,
                    {"score": {"$meta": "textScore"}},
                )
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit)
            )
        except Exception:
            # Regex fallback
            pattern = "|".join(keywords[:5])
            text_filter = {**filters, "content": {"$regex": pattern, "$options": "i"}}
            cursor = collection.find(text_filter).limit(limit)

        results = []
        async for doc in cursor:
            results.append(
                {
                    "chunk_id": str(doc["_id"]),
                    "document_id": str(doc["document_id"]),
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "chunk_index": doc.get("chunk_index", 0),
                    "score": doc.get("score", 1.0),
                    "search_type": "keyword",
                }
            )
        return results

    def _reciprocal_rank_fusion(
        self,
        list_a: List[Dict],
        list_b: List[Dict],
    ) -> List[Dict]:
        """Merge two ranked lists using Reciprocal Rank Fusion."""
        scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict] = {}

        for rank, item in enumerate(list_a):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
            chunk_map[cid] = item

        for rank, item in enumerate(list_b):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
            chunk_map[cid] = item

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        results = []
        for cid in sorted_ids:
            item = chunk_map[cid].copy()
            item["rrf_score"] = scores[cid]
            item["score"] = scores[cid]
            results.append(item)
        return results

    async def _rerank(
        self,
        query: str,
        candidates: List[Dict],
    ) -> List[Dict]:
        """Cross-encoder reranking for precision."""
        if not candidates:
            return candidates
        try:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            pairs = [(query, c["content"]) for c in candidates]
            ce_scores = model.predict(pairs)

            for item, score in zip(candidates, ce_scores):
                item["score"] = float(score)

            candidates.sort(key=lambda x: x["score"], reverse=True)
        except Exception as e:
            logger.warning("Cross-encoder reranking failed", error=str(e))
        return candidates


retrieval_service = RetrievalService()
