"""Integration tests for grids API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import GameDefinition
from app.models.grid import ScoredGrid
from app.models.statistics import StatisticsSnapshot


@pytest.fixture
async def game_with_snapshot_for_scoring(db_session: AsyncSession):
    """Create a game with a statistics snapshot suitable for grid scoring."""
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
        description="Test game for scoring",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)

    # Create a full statistics snapshot with all 49 numbers
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


@pytest.fixture
async def game_with_top_grids(db_session: AsyncSession, game_with_snapshot_for_scoring):
    """Create a game with some pre-scored top grids."""
    game, snapshot = game_with_snapshot_for_scoring
    grids = []
    for i in range(3):
        grid = ScoredGrid(
            game_id=game.id,
            numbers=[5 + i, 12, 23, 34, 47],
            stars=[3],
            total_score=0.85 - i * 0.1,
            score_breakdown={
                "frequency": 0.8,
                "gap": 0.7,
                "cooccurrence": 0.6,
                "structure": 0.75,
                "balance": 0.9,
                "pattern_penalty": 0.05,
            },
            rank=i + 1,
            method="genetic_algorithm",
            computed_at=datetime.now(UTC),
            is_top=True,
        )
        db_session.add(grid)
        grids.append(grid)
    await db_session.flush()
    for g in grids:
        await db_session.refresh(g)
    return game, grids


class TestGridsAPI:
    @pytest.mark.asyncio
    async def test_score_grid(self, db_session, game_with_snapshot_for_scoring):
        """POST /grids/score returns a valid score."""
        import app.models.base as base_module

        game, snapshot = game_with_snapshot_for_scoring
        session_factory = type(db_session)

        original_engine = base_module._engine
        original_factory = base_module._session_factory

        engine = db_session.bind
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/grids/score",
                    json={"numbers": [5, 12, 23, 34, 47]},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert "total_score" in data
            assert 0 <= data["total_score"] <= 1
            assert "score_breakdown" in data
            assert set(data["score_breakdown"].keys()) == {
                "frequency",
                "gap",
                "cooccurrence",
                "structure",
                "balance",
                "pattern_penalty",
            }
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_score_grid_with_profile(self, db_session, game_with_snapshot_for_scoring):
        """POST /grids/score with profile parameter."""
        import app.models.base as base_module

        game, snapshot = game_with_snapshot_for_scoring
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/grids/score",
                    json={"numbers": [5, 12, 23, 34, 47], "profile": "tendance"},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert 0 <= data["total_score"] <= 1
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_score_grid_no_snapshot(self, db_session):
        """POST /grids/score returns 422 when no statistics available."""
        import app.models.base as base_module

        # Create a game without any statistics snapshot
        game = GameDefinition(
            name="Empty Game",
            slug="empty",
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
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/grids/score",
                    json={"numbers": [1, 2, 3, 4, 5]},
                )
            assert resp.status_code == 422
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_get_top_grids(self, db_session, game_with_top_grids):
        """GET /grids/top returns scored grids."""
        import app.models.base as base_module

        game, grids = game_with_top_grids
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/v1/games/{game.id}/grids/top?limit=10")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 3
            # Ordered by score desc
            assert data[0]["total_score"] >= data[1]["total_score"]
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_get_grid_by_id(self, db_session, game_with_top_grids):
        """GET /grids/{grid_id} returns a single grid."""
        import app.models.base as base_module

        game, grids = game_with_top_grids
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/v1/games/{game.id}/grids/{grids[0].id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["numbers"] == grids[0].numbers
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_get_grid_not_found(self, db_session, game_with_snapshot_for_scoring):
        """GET /grids/{grid_id} returns 404 for non-existent grid."""
        import app.models.base as base_module

        game, _ = game_with_snapshot_for_scoring
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/v1/games/{game.id}/grids/99999")
            assert resp.status_code == 404
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_generate_grids(self, db_session, game_with_snapshot_for_scoring):
        """POST /grids/generate returns generated grids."""
        import app.models.base as base_module

        game, snapshot = game_with_snapshot_for_scoring
        engine = db_session.bind
        original_engine = base_module._engine
        original_factory = base_module._session_factory
        base_module._engine = engine
        base_module._session_factory = lambda: type(db_session)(bind=engine, expire_on_commit=False)

        try:
            from app.main import create_app

            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/grids/generate",
                    json={"count": 3, "method": "annealing"},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert "grids" in data
            assert len(data["grids"]) == 3
            assert "method_used" in data
            assert data["method_used"] == "annealing"
            assert data["computation_time_ms"] > 0
            for g in data["grids"]:
                assert 0 <= g["total_score"] <= 1
                assert len(g["numbers"]) == 5
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory

    @pytest.mark.asyncio
    async def test_generate_grids_no_snapshot(self, db_session):
        """POST /grids/generate returns 422 when no statistics available."""
        import app.models.base as base_module

        game = GameDefinition(
            name="Empty Game 2",
            slug="empty2",
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
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    f"/api/v1/games/{game.id}/grids/generate",
                    json={"count": 3},
                )
            assert resp.status_code == 422
        finally:
            base_module._engine = original_engine
            base_module._session_factory = original_factory
