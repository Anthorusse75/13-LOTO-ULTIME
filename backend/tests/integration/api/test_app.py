"""Integration tests for the FastAPI application."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.models.base import Base, close_db, init_db


@pytest.fixture
async def client():
    """Create a fresh test client for each test."""
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-min-32-chars!!"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

    from app.main import create_app

    test_app = create_app()

    # Manually initialize the DB since ASGITransport doesn't trigger lifespan
    init_db("sqlite+aiosqlite:///:memory:")
    from app.models.base import _engine as eng

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await close_db()


class TestHealthEndpoint:
    async def test_health_returns_healthy(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    async def test_health_has_security_headers(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"

    async def test_health_has_timing_header(self, client: AsyncClient):
        response = await client.get("/health")
        assert "x-process-time-ms" in response.headers

    async def test_health_has_request_id(self, client: AsyncClient):
        response = await client.get("/health")
        assert "x-request-id" in response.headers


class TestGamesEndpoint:
    async def test_list_games_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/games")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_game_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/games/nonexistent")
        assert response.status_code == 404


class TestSwaggerDocs:
    async def test_openapi_schema(self, client: AsyncClient):
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "LOTO ULTIME"
