"""Tests for SimulationService."""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.engines.simulation import SimulationResult, PortfolioSimulationResult, StabilityResult, ComparisonResult
from app.models.statistics import StatisticsSnapshot
from app.services.simulation import SimulationService


@pytest.fixture
def small_config():
    return GameConfig(
        name="Test",
        slug="test",
        numbers_pool=10,
        numbers_drawn=3,
        min_number=1,
        max_number=10,
    )


@pytest.fixture
def mock_snapshot():
    snapshot = MagicMock(spec=StatisticsSnapshot)
    snapshot.frequencies = {
        str(n): {"count": 10, "relative": 0.3, "ratio": 1.0, "last_seen": 0}
        for n in range(1, 11)
    }
    snapshot.gaps = {
        str(n): {
            "current_gap": 2,
            "avg_gap": 3.0,
            "max_gap": 8,
            "min_gap": 1,
            "median_gap": 3.0,
            "expected_gap": 3.3,
        }
        for n in range(1, 11)
    }
    snapshot.cooccurrence_matrix = {
        "pairs": {},
        "expected_pair_count": 5.0,
        "matrix_shape": [10, 10],
    }
    return snapshot


@pytest.fixture
def mock_draws():
    """50 random draws for the small game."""
    rng = np.random.default_rng(42)
    draws = []
    for _ in range(50):
        draw = sorted(rng.choice(np.arange(1, 11), size=3, replace=False).tolist())
        draws.append(draw)
    return np.array(draws)


@pytest.fixture
def mock_repos(mock_snapshot, mock_draws):
    stats_repo = AsyncMock()
    stats_repo.get_latest = AsyncMock(return_value=mock_snapshot)
    draw_repo = AsyncMock()
    draw_repo.get_numbers_matrix = AsyncMock(return_value=mock_draws)
    return draw_repo, stats_repo


class TestSimulationService:
    @pytest.mark.asyncio
    async def test_simulate_grid(self, small_config, mock_repos):
        draw_repo, stats_repo = mock_repos
        service = SimulationService(draw_repo, stats_repo)

        result, elapsed_ms = await service.simulate_grid(
            game_id=1, game=small_config, grid=[1, 2, 3], n_simulations=500, seed=42
        )

        assert isinstance(result, SimulationResult)
        assert result.n_simulations == 500
        assert elapsed_ms > 0

    @pytest.mark.asyncio
    async def test_simulate_portfolio(self, small_config, mock_repos):
        draw_repo, stats_repo = mock_repos
        service = SimulationService(draw_repo, stats_repo)

        result, elapsed_ms = await service.simulate_portfolio(
            game_id=1,
            game=small_config,
            portfolio=[[1, 2, 3], [4, 5, 6]],
            n_simulations=500,
            seed=42,
        )

        assert isinstance(result, PortfolioSimulationResult)
        assert 0.0 <= result.hit_rate <= 1.0
        assert elapsed_ms > 0

    @pytest.mark.asyncio
    async def test_analyze_stability(self, small_config, mock_repos):
        draw_repo, stats_repo = mock_repos
        service = SimulationService(draw_repo, stats_repo)

        result, elapsed_ms = await service.analyze_stability(
            game_id=1, game=small_config, grid=[1, 5, 10], n_bootstrap=20, seed=42
        )

        assert isinstance(result, StabilityResult)
        assert 0.0 <= result.stability <= 1.0
        assert elapsed_ms > 0
        draw_repo.get_numbers_matrix.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_analyze_stability_insufficient_draws(self, small_config):
        draw_repo = AsyncMock()
        draw_repo.get_numbers_matrix = AsyncMock(return_value=np.array([[1, 2, 3]] * 5))
        stats_repo = AsyncMock()
        service = SimulationService(draw_repo, stats_repo)

        with pytest.raises(InsufficientDataError, match="at least 30"):
            await service.analyze_stability(
                game_id=1, game=small_config, grid=[1, 2, 3], n_bootstrap=20
            )

    @pytest.mark.asyncio
    async def test_compare_with_random(self, small_config, mock_repos):
        draw_repo, stats_repo = mock_repos
        service = SimulationService(draw_repo, stats_repo)

        result, elapsed_ms = await service.compare_with_random(
            game_id=1, game=small_config, grid=[1, 5, 10], n_random=200, seed=42
        )

        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.percentile <= 100.0
        assert elapsed_ms > 0

    @pytest.mark.asyncio
    async def test_compare_with_random_no_snapshot(self, small_config):
        draw_repo = AsyncMock()
        stats_repo = AsyncMock()
        stats_repo.get_latest = AsyncMock(return_value=None)
        service = SimulationService(draw_repo, stats_repo)

        with pytest.raises(InsufficientDataError, match="No statistics snapshot"):
            await service.compare_with_random(
                game_id=1, game=small_config, grid=[1, 2, 3], n_random=100
            )
