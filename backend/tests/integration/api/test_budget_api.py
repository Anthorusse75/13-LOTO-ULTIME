"""Integration tests for budget API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.main import create_app
from app.models.game import GameDefinition
from app.models.statistics import StatisticsSnapshot
from tests.integration.api.conftest import override_auth


def _override_db(test_session: AsyncSession):
    async def _fake_get_db():
        yield test_session

    return _fake_get_db


@pytest.fixture
async def game_with_stats(db_session: AsyncSession):
    """Create a game with statistics snapshot needed by GridService."""
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

    # Build frequencies / gaps / cooccurrence for all 49 numbers
    frequencies = {
        str(n): {"count": 50 + n, "ratio": (50 + n) / 500, "last_draw_index": 1}
        for n in range(1, 50)
    }
    gaps = {
        str(n): {
            "current_gap": n % 10 + 1,
            "max_gap": 20,
            "avg_gap": 10.0,
            "min_gap": 1,
            "median_gap": 9.0,
            "expected_gap": 9.8,
        }
        for n in range(1, 50)
    }
    cooc_pairs = {}
    for i in range(1, 50):
        for j in range(i + 1, 50):
            cooc_pairs[f"{i}-{j}"] = {
                "count": (i + j) % 10,
                "expected": 5.0,
                "affinity": round(((i + j) % 10) / 5.0, 4),
            }

    snapshot = StatisticsSnapshot(
        game_id=game.id,
        computed_at=datetime.now(UTC),
        draw_count=100,
        frequencies=frequencies,
        gaps=gaps,
        cooccurrence_matrix={
            "pairs": cooc_pairs,
            "expected_pair_count": 5.0,
            "matrix_shape": [49, 49],
        },
        temporal_trends={"windows": []},
        distribution_stats={"entropy": 5.6},
        bayesian_priors={},
        graph_metrics={},
    )
    db_session.add(snapshot)
    await db_session.flush()
    return game


def _make_app(db_session: AsyncSession, role: str = "UTILISATEUR"):
    app = create_app()
    override_auth(app, role=role)
    app.dependency_overrides[get_db] = _override_db(db_session)
    return app


OPTIMIZE_PAYLOAD = {
    "budget": 22.0,
    "objective": "balanced",
}


@pytest.mark.asyncio
async def test_budget_optimize(db_session, game_with_stats):
    """POST /budget/optimize → 200 with recommendations."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=OPTIMIZE_PAYLOAD,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["budget"] == 22.0
    assert data["grid_price"] > 0
    assert data["max_grids"] >= 1
    assert len(data["recommendations"]) >= 1
    # At least one should be marked recommended
    assert any(r["is_recommended"] for r in data["recommendations"])
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_budget_optimize_with_numbers(db_session, game_with_stats):
    """POST /budget/optimize with numbers → includes wheeling strategy."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    payload = {
        "budget": 50.0,
        "objective": "coverage",
        "numbers": [1, 2, 3, 4, 5, 6, 7, 8],
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=payload,
        )
    assert resp.status_code == 200
    data = resp.json()
    strategies = [r["strategy"] for r in data["recommendations"]]
    assert "wheeling" in strategies


@pytest.mark.asyncio
async def test_budget_history(db_session, game_with_stats):
    """Optimize then list → should find the plan."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First optimize
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=OPTIMIZE_PAYLOAD,
        )
        assert gen_resp.status_code == 200
        plan_id = gen_resp.json()["id"]

        # List history
        resp = await client.get(f"/api/v1/games/{game.id}/budget/history")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(p["id"] == plan_id for p in data)


@pytest.mark.asyncio
async def test_budget_get_by_id(db_session, game_with_stats):
    """GET /budget/{id} → 200 with plan details."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=OPTIMIZE_PAYLOAD,
        )
        plan_id = gen_resp.json()["id"]

        resp = await client.get(f"/api/v1/games/{game.id}/budget/{plan_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == plan_id
    assert data["budget"] == 22.0


@pytest.mark.asyncio
async def test_budget_delete(db_session, game_with_stats):
    """DELETE /budget/{id} → 204."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gen_resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=OPTIMIZE_PAYLOAD,
        )
        plan_id = gen_resp.json()["id"]

        resp = await client.delete(f"/api/v1/games/{game.id}/budget/{plan_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_budget_insufficient_budget(db_session, game_with_stats):
    """POST /budget/optimize with tiny budget → 422."""
    game = game_with_stats
    app = _make_app(db_session)
    transport = ASGITransport(app=app)
    payload = {"budget": 0.50, "objective": "balanced"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/games/{game.id}/budget/optimize",
            json=payload,
        )
    assert resp.status_code == 422
