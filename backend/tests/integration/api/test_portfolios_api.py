"""Integration tests for portfolios API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import GameDefinition
from app.models.statistics import StatisticsSnapshot
from tests.integration.api.conftest import override_auth


@pytest.fixture
async def game_with_snapshot_for_portfolio(db_session: AsyncSession):
    """Create a game with statistics for portfolio generation."""
    game = GameDefinition(
        name="Loto Portfolio",
        slug="loto-portfolio",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="chance",
        draw_frequency="lun/mer/sam",
        historical_source="fdj",
        description="Test game for portfolio",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)

    frequencies = {
        str(n): {
            "count": 10 + (n % 7),
            "relative": round((10 + n % 7) / 100, 6),
            "ratio": round((10 + n % 7) / 100 / (5 / 49), 4),
            "last_seen": n % 10,
        }
        for n in range(1, 50)
    }
    gaps = {
        str(n): {
            "current_gap": n % 10,
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
    await db_session.refresh(snapshot)
    return game, snapshot


class TestPortfoliosAPI:
    @pytest.mark.asyncio
    async def test_generate_portfolio(self, db_session, game_with_snapshot_for_portfolio):
        """POST /portfolios/generate returns an optimized portfolio."""
        import app.models.base as base_module

        game, snapshot = game_with_snapshot_for_portfolio
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            override_auth(test_app)
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/portfolios/generate",
                    json={"grid_count": 3, "strategy": "balanced"},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["strategy"] == "balanced"
            assert data["grid_count"] == 3
            assert len(data["grids"]) == 3
            assert data["diversity_score"] >= 0
            assert data["coverage_score"] >= 0
            assert data["avg_grid_score"] > 0
            assert data["computation_time_ms"] > 0
            for g in data["grids"]:
                assert "numbers" in g
                assert "score" in g
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_generate_portfolio_max_diversity(
        self, db_session, game_with_snapshot_for_portfolio
    ):
        """POST /portfolios/generate with max_diversity strategy."""
        import app.models.base as base_module

        game, snapshot = game_with_snapshot_for_portfolio
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            override_auth(test_app)
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/portfolios/generate",
                    json={"grid_count": 5, "strategy": "max_diversity"},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["strategy"] == "max_diversity"
            assert len(data["grids"]) == 5
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_generate_portfolio_no_snapshot(self, db_session):
        """POST /portfolios/generate returns 422 when no statistics available."""
        import app.models.base as base_module

        game = GameDefinition(
            name="Empty Portfolio",
            slug="empty-portfolio",
            numbers_pool=49,
            numbers_drawn=5,
            min_number=1,
            max_number=49,
            draw_frequency="test",
            historical_source="test",
            description="test",
            is_active=True,
        )
        db_session.add(game)
        await db_session.flush()
        await db_session.refresh(game)

        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            override_auth(test_app)
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/portfolios/generate",
                    json={"grid_count": 5, "strategy": "balanced"},
                )
            assert resp.status_code == 422
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory
