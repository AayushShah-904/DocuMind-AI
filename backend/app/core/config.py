from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "DocuMind AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "documind"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Gemini ────────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str

    # ── File Upload ───────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ── Embedding ─────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # ── Chunking ──────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # ── Retrieval ─────────────────────────────────────────────────────────────
    TOP_K: int = 5

    # ── Computed Properties ───────────────────────────────────────────────────
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
