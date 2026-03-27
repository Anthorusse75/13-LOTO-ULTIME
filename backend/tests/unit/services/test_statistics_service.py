"""Tests for StatisticsService."""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from app.core.exceptions import EngineComputationError, InsufficientDataError
from app.core.game_definitions import GameConfig
from app.services.statistics import StatisticsService


@pytest.fixture
def game_config() -> GameConfig:
    return GameConfig(
        name="Mini Loto",
        slug="mini-loto",
        numbers_pool=10,
        numbers_drawn=3,
        min_number=1,
        max_number=10,
    )


@pytest.fixture
def draws_matrix() -> np.ndarray:
    return np.array(
        [
            [1, 3, 7],
            [2, 5, 9],
            [1, 4, 8],
            [3, 6, 10],
            [1, 5, 7],
            [2, 3, 9],
            [4, 7, 10],
            [1, 6, 8],
            [3, 5, 9],
            [2, 7, 10],
        ]
    )


@pytest.fixture
def draw_repo(draws_matrix):
    repo = AsyncMock()
    repo.get_numbers_matrix = AsyncMock(return_value=draws_matrix)
    return repo


@pytest.fixture
def stats_repo():
    repo = AsyncMock()

    async def mock_create(snapshot):
        snapshot.id = 1
        return snapshot

    repo.create = mock_create
    repo.get_latest = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def service(draw_repo, stats_repo):
    return StatisticsService(draw_repo, stats_repo)


class TestStatisticsServiceComputeAll:
    @pytest.mark.asyncio
    async def test_compute_all_success(self, service, game_config):
        snapshot = await service.compute_all(game_id=1, game=game_config)
        assert snapshot.game_id == 1
        assert snapshot.draw_count == 10
        assert snapshot.frequencies is not None
        assert snapshot.gaps is not None
        assert snapshot.cooccurrence_matrix is not None
        assert snapshot.temporal_trends is not None
        assert snapshot.distribution_stats is not None
        assert snapshot.bayesian_priors is not None
        assert snapshot.graph_metrics is not None

    @pytest.mark.asyncio
    async def test_compute_all_frequencies_correct(self, service, game_config):
        snapshot = await service.compute_all(game_id=1, game=game_config)
        # Number 1 appears 4 times
        assert snapshot.frequencies[1]["count"] == 4

    @pytest.mark.asyncio
    async def test_insufficient_data(self, stats_repo, game_config):
        draw_repo = AsyncMock()
        draw_repo.get_numbers_matrix = AsyncMock(return_value=np.array([[1, 2, 3]]))
        svc = StatisticsService(draw_repo, stats_repo)
        with pytest.raises(InsufficientDataError):
            await svc.compute_all(game_id=1, game=game_config)

    @pytest.mark.asyncio
    async def test_engine_failure_propagates(self, service, game_config):
        # Replace one engine with a broken one
        broken = MagicMock()
        broken.compute = MagicMock(side_effect=ValueError("boom"))
        broken.get_name = MagicMock(return_value="broken")
        service._engines["frequency"] = broken

        with pytest.raises(EngineComputationError, match="frequency"):
            await service.compute_all(game_id=1, game=game_config)


class TestStatisticsServiceGetLatest:
    @pytest.mark.asyncio
    async def test_get_latest_none(self, service):
        result = await service.get_latest(game_id=1)
        assert result is None


class TestStatisticsServiceComputeSingle:
    def test_compute_single_frequency(self, service, game_config):
        draws = np.array([[1, 3, 7], [2, 5, 9], [1, 4, 8]] * 4)
        result = service.compute_single("frequency", draws, game_config)
        assert 1 in result
        assert result[1]["count"] > 0

    def test_compute_single_unknown_engine(self, service, game_config):
        with pytest.raises(EngineComputationError, match="Unknown engine"):
            service.compute_single("nonexistent", np.array([]), game_config)
