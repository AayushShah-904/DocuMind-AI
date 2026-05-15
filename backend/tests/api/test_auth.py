"""API tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(test_client: AsyncClient):
    resp = await test_client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "Test1234!", "full_name": "New User"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "Test1234!"}
    await test_client.post("/api/v1/auth/register", json=payload)
    resp = await test_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient):
    await test_client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "Test1234!"},
    )
    resp = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Test1234!"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(test_client: AsyncClient):
    resp = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_me_requires_auth(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/auth/me")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_me_with_auth(test_client: AsyncClient, auth_headers):
    resp = await test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "email" in resp.json()
