"""Integration tests for the Jobs API endpoints."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.models.base import Base, close_db, init_db
from tests.integration.api.conftest import override_auth


@pytest.fixture
async def client():
    """Create a fresh test client for each test."""
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-min-32-chars!!"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

    from app.main import create_app

    test_app = create_app()
    override_auth(test_app)

    init_db("sqlite+aiosqlite:///:memory:")
    from app.models.base import _engine as eng

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await close_db()


class TestJobsListEndpoint:
    async def test_list_jobs_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_jobs_pagination(self, client: AsyncClient):
        response = await client.get("/api/v1/jobs?limit=10&offset=0")
        assert response.status_code == 200


class TestJobsStatusEndpoint:
    async def test_status_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/jobs/status")
        assert response.status_code == 200
        data = response.json()
        assert "running_jobs" in data
        assert "running_count" in data
        assert data["running_count"] == 0
        assert "last_runs" in data


class TestJobsTriggerEndpoint:
    async def test_trigger_unknown_job(self, client: AsyncClient):
        response = await client.post("/api/v1/jobs/unknown_job/trigger")
        assert response.status_code == 404
        assert "Unknown job" in response.json()["detail"]


class TestJobsHistoryEndpoint:
    async def test_history_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/jobs/nonexistent/history")
        assert response.status_code == 404
