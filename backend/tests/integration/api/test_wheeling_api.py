"""Integration tests for wheeling API endpoints (TEST-11/12/13)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.main import create_app
from app.models.game import GameDefinition
from app.models.prize_tier import GamePrizeTier
from tests.integration.api.conftest import override_auth


def _override_db(test_session: AsyncSession):
    async def _fake_get_db():
        yield test_session

    return _fake_get_db


@pytest.fixture
async def game(db_session: AsyncSession) -> GameDefinition:
    game = GameDefinition(
        name="Loto FDJ",
        slug="loto_fdj",
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
    # Add prize tiers
    for tier_data in [
        {"rank": 1, "name": "5+chance", "match_numbers": 5, "match_stars": 1, "avg_prize": 2_000_000, "probability": 0.00000005},
        {"rank": 2, "name": "5", "match_numbers": 5, "match_stars": 0, "avg_prize": 100_000, "probability": 0.0000005},
        {"rank": 3, "name": "4+chance", "match_numbers": 4, "match_stars": 1, "avg_prize": 1_000, "probability": 0.00001},
        {"rank": 4, "name": "4", "match_numbers": 4, "match_stars": 0, "avg_prize": 500, "probability": 0.0001},
        {"rank": 5, "name": "3+chance", "match_numbers": 3, "match_stars": 1, "avg_prize": 50, "probability": 0.001},
        {"rank": 6, "name": "3", "match_numbers": 3, "match_stars": 0, "avg_prize": 5, "probability": 0.01},
    ]:
        db_session.add(GamePrizeTier(game_id=game.id, **tier_data))
    await db_session.flush()
    return game


def _make_app(db_session: AsyncSession, role: str = "UTILISATEUR"):
    app = create_app()
    override_auth(app, role=role)
    app.dependency_overrides[get_db] = _override_db(db_session)
    return app


PREVIEW_PAYLOAD = {
    "numbers": [1, 2, 3, 4, 5, 6, 7, 8],
    "stars": None,
    "guarantee": 2,
}

GENERATE_PAYLOAD = {
    "numbers": [1, 2, 3, 4, 5, 6, 7, 8],
    "stars": None,
    "guarantee": 2,
}


@pytest.mark.asyncio
async def test_wheeling_preview(db_session, game):
    """POST /wheeling/preview → 200 with estimation."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/preview",
            json=PREVIEW_PAYLOAD,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_grid_count"] >= 1
    assert data["estimated_cost"] > 0
    assert data["full_wheel_size"] == 56  # C(8,5)
    assert data["total_t_combinations"] == 28  # C(8,2)


@pytest.mark.asyncio
async def test_wheeling_generate(db_session, game):
    """POST /wheeling/generate → 200 with grids and metrics."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/generate",
            json=GENERATE_PAYLOAD,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grid_count"] > 0
    assert data["coverage_rate"] == 1.0
    assert data["total_cost"] > 0
    assert len(data["grids"]) == data["grid_count"]
    assert data["id"] is not None  # persisted
    assert len(data["gain_scenarios"]) > 0


@pytest.mark.asyncio
async def test_wheeling_history(db_session, game):
    """Generate then list → should find the system."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First generate
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/generate",
            json=GENERATE_PAYLOAD,
        )
        assert gen_resp.status_code == 200
        system_id = gen_resp.json()["id"]

        # List history
        resp = await client.get(f"/api/v1/games/{game.id}/wheeling/history")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"] == system_id


@pytest.mark.asyncio
async def test_wheeling_get_by_id(db_session, game):
    """Generate then GET by ID."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/generate",
            json=GENERATE_PAYLOAD,
        )
        system_id = gen_resp.json()["id"]
        resp = await client.get(f"/api/v1/games/{game.id}/wheeling/{system_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == system_id
    assert data["guarantee_level"] == 2


@pytest.mark.asyncio
async def test_wheeling_delete(db_session, game):
    """Generate then DELETE."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/generate",
            json=GENERATE_PAYLOAD,
        )
        system_id = gen_resp.json()["id"]
        resp = await client.delete(f"/api/v1/games/{game.id}/wheeling/{system_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_wheeling_validate_too_many_numbers(db_session, game):
    """More than 20 numbers → 422."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/preview",
            json={"numbers": list(range(1, 22)), "guarantee": 2},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_wheeling_validate_t_greater_than_k(db_session, game):
    """Guarantee t > k → 422."""
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/wheeling/preview",
            json={"numbers": [1, 2, 3, 4, 5, 6, 7], "guarantee": 6},
        )
    assert resp.status_code == 422
