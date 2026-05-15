
import motor.motor_asyncio
from beanie import init_beanie

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: motor.motor_asyncio.AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global _client

    # Import models here to avoid circular imports
    from app.models.chat_session import ChatSession
    from app.models.chunk import DocumentChunk
    from app.models.document import Document_
    from app.models.message import Message
    from app.models.user import User

    logger.info("Connecting to MongoDB Atlas...")
    import certifi

    _client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URI, tlsCAFile=certifi.where()
    )
    db = _client[settings.MONGODB_DB_NAME]

    await init_beanie(
        database=db,
        document_models=[User, Document_, DocumentChunk, ChatSession, Message],
    )
    logger.info("MongoDB connected", db=settings.MONGODB_DB_NAME)


async def disconnect_db() -> None:
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB disconnected")


def get_db_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _client
