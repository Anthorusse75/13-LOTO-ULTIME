"""Integration tests for statistics API endpoints."""

from datetime import UTC, date, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.models.game import GameDefinition
from app.models.statistics import StatisticsSnapshot
from tests.integration.api.conftest import override_auth


@pytest.fixture
async def game_with_draws(db_session: AsyncSession):
    """Create a game with 10+ draws for statistics computation."""
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

    draws_data = [
        ([3, 12, 25, 37, 44], [7]),
        ([1, 8, 19, 33, 48], [3]),
        ([5, 14, 22, 36, 41], [9]),
        ([2, 17, 28, 39, 45], [1]),
        ([7, 11, 24, 31, 49], [5]),
        ([3, 9, 18, 35, 42], [2]),
        ([6, 15, 27, 38, 46], [8]),
        ([4, 13, 23, 34, 47], [4]),
        ([10, 16, 29, 40, 43], [6]),
        ([1, 20, 26, 32, 44], [10]),
    ]

    for i, (numbers, stars) in enumerate(draws_data):
        draw = Draw(
            game_id=game.id,
            draw_date=date(2026, 1, 5 + i * 2),
            draw_number=i + 1,
            numbers=numbers,
            stars=stars,
        )
        db_session.add(draw)

    await db_session.flush()
    return game


@pytest.fixture
async def game_with_snapshot(db_session: AsyncSession, game_with_draws):
    """Create a game with a pre-computed statistics snapshot."""
    snapshot = StatisticsSnapshot(
        game_id=game_with_draws.id,
        computed_at=datetime.now(UTC),
        draw_count=10,
        frequencies={
            "1": {"count": 2, "relative": 0.2, "ratio": 1.96, "last_seen": 0},
            "3": {"count": 2, "relative": 0.2, "ratio": 1.96, "last_seen": 4},
            "7": {"count": 1, "relative": 0.1, "ratio": 0.98, "last_seen": 5},
        },
        gaps={
            "1": {
                "current_gap": 0,
                "max_gap": 7,
                "avg_gap": 3.0,
                "min_gap": 0,
                "median_gap": 3.0,
                "expected_gap": 9.8,
            },
            "3": {
                "current_gap": 4,
                "max_gap": 5,
                "avg_gap": 2.5,
                "min_gap": 0,
                "median_gap": 2.5,
                "expected_gap": 9.8,
            },
        },
        cooccurrence_matrix={
            "pairs": {
                "1-3": {"count": 0, "expected": 0.82, "affinity": 0.0},
                "1-7": {"count": 0, "expected": 0.82, "affinity": 0.0},
            },
            "expected_pair_count": 0.82,
            "matrix_shape": [49, 49],
        },
        temporal_trends={"windows": [], "momentum": {}},
        distribution_stats={
            "entropy": 5.61,
            "max_entropy": 5.6147,
            "uniformity_score": 0.9992,
            "chi2_statistic": 0.0,
            "chi2_pvalue": 1.0,
            "is_uniform": True,
            "sum_stats": {"mean": 120.5, "std": 12.0, "min": 95, "max": 145, "median": 121.0},
            "even_odd_distribution": {"mean_even": 2.5, "mean_odd": 2.5},
            "decades": {"1-10": 10, "11-20": 10, "21-30": 10, "31-40": 10, "41-49": 10},
        },
        bayesian_priors={
            "1": {
                "alpha": 2.5,
                "beta": 8.5,
                "posterior_mean": 0.227273,
                "ci_95_low": 0.05,
                "ci_95_high": 0.45,
                "ci_width": 0.4,
            },
            "3": {
                "alpha": 2.5,
                "beta": 8.5,
                "posterior_mean": 0.227273,
                "ci_95_low": 0.05,
                "ci_95_high": 0.45,
                "ci_width": 0.4,
            },
        },
        graph_metrics={
            "communities": [[1, 3, 7]],
            "centrality": {
                "1": {"degree": 0.5, "betweenness": 0.1, "eigenvector": 0.3, "community": 0},
                "3": {"degree": 0.4, "betweenness": 0.2, "eigenvector": 0.25, "community": 0},
            },
            "density": 0.42,
            "clustering_coefficient": 0.67,
        },
    )
    db_session.add(snapshot)
    await db_session.flush()
    await db_session.refresh(snapshot)
    return game_with_draws, snapshot


@pytest.fixture
async def stats_client(engine, db_session, game_with_snapshot):
    """HTTP client with a game that has a statistics snapshot loaded."""
    import os

    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-min-32-chars!!"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

    from app.main import create_app

    test_app = create_app()
    override_auth(test_app)

    # Manually init DB with the test engine
    from app.models import base as base_module

    base_module._engine = engine
    from sqlalchemy.ext.asyncio import async_sessionmaker

    base_module._session_factory = async_sessionmaker(engine, expire_on_commit=False)

    transport = ASGITransport(app=test_app)
    game, snapshot = game_with_snapshot

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, game


class TestStatisticsEndpoints:
    @pytest.mark.asyncio
    async def test_get_statistics_summary(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["game_id"] == game.id
        assert data["draw_count"] == 10
        assert "frequencies" in data
        assert "hot_numbers" in data
        assert "cold_numbers" in data

    @pytest.mark.asyncio
    async def test_get_frequencies(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/frequencies")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "number" in data[0]
        assert "count" in data[0]

    @pytest.mark.asyncio
    async def test_get_gaps(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/gaps")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_cooccurrences(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/cooccurrences")
        assert resp.status_code == 200
        data = resp.json()
        assert "pairs" in data
        assert "expected_pair_count" in data

    @pytest.mark.asyncio
    async def test_get_temporal(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/temporal")
        assert resp.status_code == 200
        data = resp.json()
        assert "windows" in data

    @pytest.mark.asyncio
    async def test_get_distribution(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/distribution")
        assert resp.status_code == 200
        data = resp.json()
        assert "entropy" in data
        assert "uniformity_score" in data
        assert "chi2_pvalue" in data

    @pytest.mark.asyncio
    async def test_get_bayesian(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/bayesian")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert "posterior_mean" in data[0]

    @pytest.mark.asyncio
    async def test_get_graph(self, stats_client):
        client, game = stats_client
        resp = await client.get(f"/api/v1/games/{game.id}/statistics/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert "communities" in data
        assert "centrality" in data
        assert "density" in data

    @pytest.mark.asyncio
    async def test_no_statistics_returns_error(self, engine, db_session):
        """Game without snapshot returns appropriate error."""
        import os

        os.environ["SECRET_KEY"] = "test-secret-key-for-testing-min-32-chars!!"
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

        game = GameDefinition(
            name="Empty Game",
            slug="empty-game",
            numbers_pool=10,
            numbers_drawn=3,
            min_number=1,
            max_number=10,
            is_active=True,
            draw_frequency="test",
            historical_source="test",
            description="test",
        )
        db_session.add(game)
        await db_session.flush()
        await db_session.refresh(game)

        from sqlalchemy.ext.asyncio import async_sessionmaker

        from app.main import create_app
        from app.models import base as base_module

        test_app = create_app()
        base_module._engine = engine
        base_module._session_factory = async_sessionmaker(engine, expire_on_commit=False)

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/games/{game.id}/statistics/")
            assert resp.status_code == 422 or resp.status_code == 400
