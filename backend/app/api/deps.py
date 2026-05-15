"""
FastAPI dependency injection: current user, admin check, rate limiting.
"""

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import http_401, http_403, http_429
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.services.cache_service import cache_service

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if not credentials:
        raise http_401("No authentication token provided.")

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload["sub"]
    except Exception:
        raise http_401("Invalid or expired token.")

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise http_401("User account not found or deactivated.")

    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise http_403("Admin access required.")
    return current_user


async def check_rate_limit(
    current_user: User = Depends(get_current_user),
) -> User:
    allowed, remaining = cache_service.check_rate_limit(
        identifier=str(current_user.id),
        limit=60,
        window_seconds=60,
    )
    if not allowed:
        raise http_429()
    return current_user
