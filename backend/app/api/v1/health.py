import time

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.mongodb import get_db_client
from app.core.config import settings

router = APIRouter(tags=["System"])


class HealthResponse(BaseModel):
    status: str
    version: str
    db: str
    uptime_ms: int


_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health():
    """System health check — used by load balancers and monitoring."""
    db_status = "ok"
    try:
        client = get_db_client()
        await client[settings.MONGODB_DB_NAME].command("ping")
    except Exception:
        db_status = "unreachable"

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        db=db_status,
        uptime_ms=int((time.time() - _start_time) * 1000),
    )
