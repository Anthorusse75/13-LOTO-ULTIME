"""Grid service — scoring orchestration and persistence."""

from datetime import UTC, datetime

import structlog

from app.core.exceptions import GameNotFoundError, InsufficientDataError
from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult
from app.models.grid import ScoredGrid
from app.repositories.grid_repository import GridRepository
from app.repositories.statistics_repository import StatisticsRepository

logger = structlog.get_logger(__name__)


class GridService:
    """Score grids against the latest statistics snapshot."""

    def __init__(
        self,
        stats_repo: StatisticsRepository,
        grid_repo: GridRepository,
    ):
        self._stats_repo = stats_repo
        self._grid_repo = grid_repo

    async def score_grid(
        self,
        game_id: int,
        game: GameConfig,
        numbers: list[int],
        stars: list[int] | None = None,
        profile: str = "equilibre",
        custom_weights: dict[str, float] | None = None,
    ) -> ScoredResult:
        """Score a single grid against the latest statistics."""
        snapshot = await self._stats_repo.get_latest(game_id)
        if snapshot is None:
            raise InsufficientDataError(
                "No statistics snapshot available. Run statistics computation first."
            )

        statistics = {
            "frequency": snapshot.frequencies,
            "gaps": snapshot.gaps,
            "cooccurrence": snapshot.cooccurrence_matrix,
        }

        if custom_weights:
            scorer = GridScorer(weights=custom_weights)
        else:
            scorer = GridScorer.from_profile(profile)

        if stars and game.stars_pool:
            return scorer.score_with_stars(numbers, stars, statistics, game)
        return scorer.score(numbers, statistics, game)

    async def get_top_grids(
        self, game_id: int, limit: int = 10
    ) -> list[ScoredGrid]:
        """Return the top-scored grids for a game."""
        return await self._grid_repo.get_top_grids(game_id, limit)

    async def get_grid(self, grid_id: int) -> ScoredGrid | None:
        """Return a single grid by ID."""
        return await self._grid_repo.get(grid_id)
