"""
Tests conftest: shared fixtures for API and unit tests.
Uses mongomock-motor for in-memory MongoDB and fakeredis for Redis.
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db import mongodb
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_client():
    """Async test client with in-memory MongoDB."""
    import mongomock_motor

    # Patch the MongoDB connection to use mongomock
    original_connect = mongodb.connect_db

    async def mock_connect():
        from beanie import init_beanie

        from app.models.chat_session import ChatSession
        from app.models.chunk import DocumentChunk
        from app.models.document import Document_
        from app.models.message import Message
        from app.models.user import User

        client = mongomock_motor.AsyncMongoMockClient()
        db = client["test_documind"]
        await init_beanie(
            database=db,
            document_models=[User, Document_, DocumentChunk, ChatSession, Message],
        )
        mongodb._client = client

    mongodb.connect_db = mock_connect

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    mongodb.connect_db = original_connect


@pytest_asyncio.fixture
async def auth_headers(test_client: AsyncClient):
    """Register a test user and return auth headers."""
    resp = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test1234!",
            "full_name": "Test User",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
