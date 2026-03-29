"""Integration tests for simulation API endpoints."""

from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.models.game import GameDefinition
from app.models.statistics import StatisticsSnapshot
from tests.integration.api.conftest import override_auth


@pytest.fixture
async def game_with_data_for_simulation(db_session: AsyncSession):
    """Create a game with statistics and 50 draws for simulation tests."""
    game = GameDefinition(
        name="Loto Simulation",
        slug="loto-simulation",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="chance",
        draw_frequency="lun/mer/sam",
        historical_source="fdj",
        description="Test game for simulation",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)

    # Create 50 draws for bootstrap analysis
    import numpy as np

    rng = np.random.default_rng(42)
    base_date = date(2025, 1, 1)
    for i in range(50):
        numbers = sorted(rng.choice(np.arange(1, 50), size=5, replace=False).tolist())
        draw = Draw(
            game_id=game.id,
            draw_date=base_date + timedelta(days=i),
            draw_number=i + 1,
            numbers=numbers,
            stars=[int(rng.integers(1, 11))],
        )
        db_session.add(draw)

    # Create statistics snapshot
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
    for i in range(1, 10):
        for j in range(i + 1, 10):
            cooc_pairs[f"{i}-{j}"] = {
                "count": (i + j) % 10,
                "expected": 5.0,
                "affinity": round(((i + j) % 10) / 5.0, 4),
            }

    snapshot = StatisticsSnapshot(
        game_id=game.id,
        computed_at=datetime.now(UTC),
        draw_count=50,
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


def _patch_base_module(db_session):
    """Patch base_module to use the test session."""
    import app.models.base as base_module

    engine = db_session.bind
    original_engine = base_module._engine
    original_factory = base_module._session_factory
    base_module._engine = engine
    base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)
    return base_module, original_engine, original_factory


def _restore_base_module(base_module, original_engine, original_factory):
    base_module._engine = original_engine
    base_module._session_factory = original_factory


class TestSimulationAPI:
    @pytest.mark.asyncio
    async def test_monte_carlo_grid(self, db_session, game_with_data_for_simulation):
        """POST /simulation/monte-carlo simulates a single grid."""
        game, _ = game_with_data_for_simulation
        base_module, orig_engine, orig_factory = _patch_base_module(db_session)

        try:
            from app.main import create_app

            _app = create_app()
            override_auth(_app)
            transport = ASGITransport(app=_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/simulation/monte-carlo",
                    json={"numbers": [1, 5, 10, 25, 49], "n_simulations": 1000, "seed": 42},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["grid"] == [1, 5, 10, 25, 49]
            assert data["n_simulations"] == 1000
            assert sum(data["match_distribution"].values()) == 1000
            assert data["avg_matches"] > 0
            assert data["computation_time_ms"] > 0
        finally:
            _restore_base_module(base_module, orig_engine, orig_factory)

    @pytest.mark.asyncio
    async def test_monte_carlo_portfolio(self, db_session, game_with_data_for_simulation):
        """POST /simulation/monte-carlo/portfolio simulates a portfolio."""
        game, _ = game_with_data_for_simulation
        base_module, orig_engine, orig_factory = _patch_base_module(db_session)

        try:
            from app.main import create_app

            _app = create_app()
            override_auth(_app)
            transport = ASGITransport(app=_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/simulation/monte-carlo/portfolio",
                    json={
                        "grids": [[1, 5, 10, 25, 49], [2, 8, 15, 30, 44]],
                        "n_simulations": 500,
                        "min_matches": 2,
                        "seed": 42,
                    },
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["n_simulations"] == 500
            assert 0.0 <= data["hit_rate"] <= 1.0
            assert data["min_matches_threshold"] == 2
            assert data["computation_time_ms"] > 0
        finally:
            _restore_base_module(base_module, orig_engine, orig_factory)

    @pytest.mark.asyncio
    async def test_stability_analysis(self, db_session, game_with_data_for_simulation):
        """POST /simulation/stability runs bootstrap analysis."""
        game, _ = game_with_data_for_simulation
        base_module, orig_engine, orig_factory = _patch_base_module(db_session)

        try:
            from app.main import create_app

            _app = create_app()
            override_auth(_app)
            transport = ASGITransport(app=_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/simulation/stability",
                    json={"numbers": [1, 5, 10, 25, 49], "n_bootstrap": 20, "seed": 42},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert 0.0 <= data["stability"] <= 1.0
            assert data["ci_95_low"] <= data["mean_score"] <= data["ci_95_high"]
            assert data["computation_time_ms"] > 0
        finally:
            _restore_base_module(base_module, orig_engine, orig_factory)

    @pytest.mark.asyncio
    async def test_compare_random(self, db_session, game_with_data_for_simulation):
        """POST /simulation/compare-random compares grid vs random."""
        game, _ = game_with_data_for_simulation
        base_module, orig_engine, orig_factory = _patch_base_module(db_session)

        try:
            from app.main import create_app

            _app = create_app()
            override_auth(_app)
            transport = ASGITransport(app=_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/simulation/compare-random",
                    json={"numbers": [1, 5, 10, 25, 49], "n_random": 200, "seed": 42},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert 0.0 <= data["percentile"] <= 100.0
            assert "z_score" in data
            assert data["computation_time_ms"] > 0
        finally:
            _restore_base_module(base_module, orig_engine, orig_factory)

    @pytest.mark.asyncio
    async def test_compare_random_no_snapshot(self, db_session):
        """POST /simulation/compare-random returns 422 with no statistics."""
        game = GameDefinition(
            name="Empty Sim",
            slug="empty-sim",
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

        base_module, orig_engine, orig_factory = _patch_base_module(db_session)

        try:
            from app.main import create_app

            _app = create_app()
            override_auth(_app)
            transport = ASGITransport(app=_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/simulation/compare-random",
                    json={"numbers": [1, 5, 10, 25, 49], "n_random": 100},
                )
            assert resp.status_code == 422
        finally:
            _restore_base_module(base_module, orig_engine, orig_factory)
