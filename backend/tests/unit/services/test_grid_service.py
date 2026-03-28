"""Tests for GridService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import ScoredResult
from app.models.statistics import StatisticsSnapshot
from app.services.grid import GridService


@pytest.fixture
def loto_config():
    return GameConfig(
        name="Loto",
        slug="loto",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="chance",
    )


@pytest.fixture
def mock_snapshot():
    """A mock StatisticsSnapshot with minimal data."""
    snapshot = MagicMock(spec=StatisticsSnapshot)
    snapshot.frequencies = {
        str(n): {"count": 10, "relative": 0.1, "ratio": 1.0, "last_seen": 0} for n in range(1, 50)
    }
    snapshot.gaps = {
        str(n): {
            "current_gap": 5,
            "avg_gap": 10.0,
            "max_gap": 20,
            "min_gap": 1,
            "median_gap": 9.0,
            "expected_gap": 9.8,
        }
        for n in range(1, 50)
    }
    snapshot.cooccurrence_matrix = {
        "pairs": {
            f"{i}-{j}": {"count": 5, "expected": 5.0, "affinity": 1.0}
            for i in range(1, 10)
            for j in range(i + 1, 10)
        },
        "expected_pair_count": 5.0,
        "matrix_shape": [49, 49],
    }
    return snapshot


@pytest.fixture
def mock_repos(mock_snapshot):
    stats_repo = AsyncMock()
    stats_repo.get_latest = AsyncMock(return_value=mock_snapshot)
    grid_repo = AsyncMock()
    grid_repo.get_top_grids = AsyncMock(return_value=[])
    grid_repo.get = AsyncMock(return_value=None)
    return stats_repo, grid_repo


class TestGridService:
    @pytest.mark.asyncio
    async def test_score_grid_basic(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.score_grid(
            game_id=1,
            game=loto_config,
            numbers=[5, 12, 23, 34, 47],
        )
        assert 0 <= result.total_score <= 1
        assert result.numbers == [5, 12, 23, 34, 47]

    @pytest.mark.asyncio
    async def test_score_grid_with_profile(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.score_grid(
            game_id=1,
            game=loto_config,
            numbers=[5, 12, 23, 34, 47],
            profile="tendance",
        )
        assert 0 <= result.total_score <= 1

    @pytest.mark.asyncio
    async def test_score_grid_with_custom_weights(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.score_grid(
            game_id=1,
            game=loto_config,
            numbers=[5, 12, 23, 34, 47],
            custom_weights={
                "frequency": 1.0,
                "gap": 0.0,
                "cooccurrence": 0.0,
                "structure": 0.0,
                "balance": 0.0,
                "pattern_penalty": 0.0,
            },
        )
        assert 0 <= result.total_score <= 1

    @pytest.mark.asyncio
    async def test_score_grid_with_stars(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.score_grid(
            game_id=1,
            game=loto_config,
            numbers=[5, 12, 23, 34, 47],
            stars=[3],
        )
        assert result.stars == [3]
        assert result.star_score is not None

    @pytest.mark.asyncio
    async def test_score_grid_no_snapshot_raises(self, loto_config):
        stats_repo = AsyncMock()
        stats_repo.get_latest = AsyncMock(return_value=None)
        grid_repo = AsyncMock()
        service = GridService(stats_repo, grid_repo)
        with pytest.raises(InsufficientDataError, match="No statistics snapshot"):
            await service.score_grid(game_id=1, game=loto_config, numbers=[1, 2, 3, 4, 5])

    @pytest.mark.asyncio
    async def test_get_top_grids(self, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.get_top_grids(game_id=1, limit=5)
        grid_repo.get_top_grids.assert_called_once_with(1, 5)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_grid(self, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result = await service.get_grid(grid_id=42)
        grid_repo.get.assert_called_once_with(42)
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_grids_auto(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        results, method_used, elapsed = await service.generate_grids(
            game_id=1, game=loto_config, count=3, method="auto", seed=42,
        )
        assert len(results) == 3
        assert isinstance(method_used, str)
        assert elapsed > 0
        for r in results:
            assert isinstance(r, ScoredResult)
            assert len(r.numbers) == loto_config.numbers_drawn

    @pytest.mark.asyncio
    async def test_generate_grids_specific_method(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        results, method_used, _ = await service.generate_grids(
            game_id=1, game=loto_config, count=2, method="annealing", seed=42,
        )
        assert method_used == "annealing"
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_generate_grids_no_snapshot_raises(self, loto_config):
        stats_repo = AsyncMock()
        stats_repo.get_latest = AsyncMock(return_value=None)
        grid_repo = AsyncMock()
        service = GridService(stats_repo, grid_repo)
        with pytest.raises(InsufficientDataError):
            await service.generate_grids(
                game_id=1, game=loto_config, count=3, method="auto",
            )

    @pytest.mark.asyncio
    async def test_generate_grids_unknown_method_raises(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        with pytest.raises(ValueError, match="Unknown method"):
            await service.generate_grids(
                game_id=1, game=loto_config, count=3, method="nonexistent",
            )

    @pytest.mark.asyncio
    async def test_generate_portfolio(self, loto_config, mock_repos):
        stats_repo, grid_repo = mock_repos
        service = GridService(stats_repo, grid_repo)
        result, method_used, elapsed = await service.generate_portfolio(
            game_id=1, game=loto_config, grid_count=3, strategy="balanced", seed=42,
        )
        assert len(result.grids) == 3
        assert result.strategy == "balanced"
        assert result.diversity_score >= 0
        assert result.coverage_score >= 0
        assert elapsed > 0
