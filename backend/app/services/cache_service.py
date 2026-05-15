"""
Redis-backed caching and rate limiting service.
Gracefully degrades if Redis is unavailable.
"""

import json
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis = None


def get_redis_client():
    global _redis
    if _redis is None:
        try:
            import redis

            _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.warning("Redis unavailable, caching disabled", error=str(e))
            _redis = None
    return _redis


class CacheService:
    def __init__(self):
        self.prefix = "documind:"
        self.default_ttl = 3600  # 1 hour

    def _key(self, *parts: str) -> str:
        return self.prefix + ":".join(parts)

    def get(self, *key_parts: str) -> Optional[Any]:
        client = get_redis_client()
        if not client:
            return None
        try:
            raw = client.get(self._key(*key_parts))
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning("Cache get failed", error=str(e))
            return None

    def set(self, *key_parts: str, value: Any, ttl: int | None = None) -> None:
        client = get_redis_client()
        if not client:
            return
        try:
            client.setex(
                self._key(*key_parts),
                ttl or self.default_ttl,
                json.dumps(value),
            )
        except Exception as e:
            logger.warning("Cache set failed", error=str(e))

    def delete(self, *key_parts: str) -> None:
        client = get_redis_client()
        if not client:
            return
        try:
            client.delete(self._key(*key_parts))
        except Exception as e:
            logger.warning("Cache delete failed", error=str(e))

    def check_rate_limit(
        self, identifier: str, limit: int = 60, window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Sliding window rate limiter.
        Returns (is_allowed, remaining_requests).
        """
        client = get_redis_client()
        if not client:
            return True, limit  # degrade gracefully

        key = self._key("ratelimit", identifier)
        try:
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()
            count = results[0]
            remaining = max(0, limit - count)
            return count <= limit, remaining
        except Exception as e:
            logger.warning("Rate limit check failed", error=str(e))
            return True, limit


cache_service = CacheService()
