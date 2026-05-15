from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.core.exceptions import http_400
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(body: RegisterRequest):
    """Create a new account and receive auth tokens."""
    try:
        _, tokens = await auth_service.register(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
        return tokens
    except Exception as e:
        raise http_400(str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Authenticate and receive auth tokens."""
    try:
        _, tokens = await auth_service.login(body.email, body.password)
        return tokens
    except Exception as e:
        raise http_400(str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    """Exchange a refresh token for a new access token."""
    try:
        return await auth_service.refresh(body.refresh_token)
    except Exception as e:
        raise http_400(str(e))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return auth_service.format_user(current_user)
