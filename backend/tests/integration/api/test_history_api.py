"""Integration tests for history API endpoints (TEST-09)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.main import create_app
from app.models.game import GameDefinition
from app.models.saved_result import UserSavedResult
from tests.integration.api.conftest import make_fake_utilisateur, override_auth


def _override_db(test_session: AsyncSession):
    async def _fake_get_db():
        yield test_session

    return _fake_get_db


@pytest.fixture
async def game(db_session: AsyncSession) -> GameDefinition:
    game = GameDefinition(
        name="Loto FDJ",
        slug="loto-fdj",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="numéro chance",
        draw_frequency="lun/mer/sam",
        historical_source="fdj",
        description="Test game",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)
    return game


def _make_app(db_session: AsyncSession, role: str = "UTILISATEUR"):
    app = create_app()
    override_auth(app, role=role)
    app.dependency_overrides[get_db] = _override_db(db_session)
    return app


SAVE_PAYLOAD = {
    "result_type": "grid",
    "parameters": {"method": "genetic_algorithm", "profile": "equilibre"},
    "result_data": {"numbers": [5, 12, 23, 34, 47], "score": 0.85},
    "name": "Ma grille test",
    "tags": ["important"],
}


@pytest.mark.asyncio
async def test_save_result(db_session, game):
    """POST /history/save — should create a saved result."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["result_type"] == "grid"
    assert data["name"] == "Ma grille test"
    assert data["is_favorite"] is False
    assert data["tags"] == ["important"]


@pytest.mark.asyncio
async def test_save_result_invalid_type(db_session, game):
    """POST /history/save — invalid result_type returns 422."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "result_type": "invalid_type", "game_id": game.id},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_results_empty(db_session, game):
    """GET /history — empty list when no results saved."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_results_with_data(db_session, game):
    """GET /history — returns saved results after saving."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id, "name": "Grille 2", "result_type": "portfolio"},
        )
        resp = await client.get("/api/v1/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_results_filter_by_type(db_session, game):
    """GET /history?result_type=grid — filters by type."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id, "result_type": "portfolio"},
        )
        resp = await client.get("/api/v1/history", params={"result_type": "grid"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["result_type"] == "grid"


@pytest.mark.asyncio
async def test_get_result(db_session, game):
    """GET /history/{id} — returns a specific result."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        result_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/history/{result_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == result_id


@pytest.mark.asyncio
async def test_get_result_not_found(db_session, game):
    """GET /history/999 — returns 404."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/history/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_result(db_session, game):
    """DELETE /history/{id} — deletes a saved result."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        result_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/history/{result_id}")
    assert resp.status_code == 204

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/history/{result_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_toggle_favorite(db_session, game):
    """PATCH /history/{id}/favorite — toggles favorite."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        result_id = create_resp.json()["id"]

        resp = await client.patch(f"/api/v1/history/{result_id}/favorite")
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch(f"/api/v1/history/{result_id}/favorite")
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is False


@pytest.mark.asyncio
async def test_update_tags(db_session, game):
    """PATCH /history/{id}/tags — updates tags."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        result_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/api/v1/history/{result_id}/tags",
            json={"tags": ["favori", "loto"]},
        )
    assert resp.status_code == 200
    assert resp.json()["tags"] == ["favori", "loto"]


@pytest.mark.asyncio
async def test_duplicate_result(db_session, game):
    """POST /history/{id}/duplicate — creates a copy."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/history/save",
            json={**SAVE_PAYLOAD, "game_id": game.id},
        )
        result_id = create_resp.json()["id"]

        resp = await client.post(f"/api/v1/history/{result_id}/duplicate")
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] != result_id
    assert "(copie)" in data["name"]
    assert data["result_type"] == "grid"


@pytest.mark.asyncio
async def test_duplicate_not_found(db_session, game):
    """POST /history/999/duplicate — returns 404."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/history/999/duplicate")
    assert resp.status_code == 404
