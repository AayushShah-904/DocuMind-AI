"""
Authentication service: registration, login, token refresh.
"""

from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.schemas.auth import TokenResponse, UserResponse

logger = get_logger(__name__)


class AuthService:
    async def register(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> tuple[User, TokenResponse]:
        if await user_repo.exists_by_email(email):
            raise ValidationError("An account with this email already exists.")

        user = await user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        logger.info("New user registered", email=email)
        tokens = self._issue_tokens(str(user.id), user.is_admin)
        return user, tokens

    async def login(self, email: str, password: str) -> tuple[User, TokenResponse]:
        user = await user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Your account has been deactivated.")

        logger.info("User logged in", user_id=str(user.id))
        tokens = self._issue_tokens(str(user.id), user.is_admin)
        return user, tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type.")
            user_id = payload["sub"]
        except Exception:
            raise UnauthorizedError("Invalid or expired refresh token.")

        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found.")

        return self._issue_tokens(user_id, user.is_admin)

    def _issue_tokens(self, user_id: str, is_admin: bool) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                subject=user_id,
                extra_claims={"admin": is_admin},
            ),
            refresh_token=create_refresh_token(subject=user_id),
        )

    def format_user(self, user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_admin=user.is_admin,
            created_at=user.created_at.isoformat(),
        )


auth_service = AuthService()
