"""Grid service — scoring, generation, and persistence."""

import asyncio
import time
from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.engines.optimization import (
    GeneticAlgorithm,
    HillClimbing,
    PortfolioOptimizer,
    PortfolioResult,
    SimulatedAnnealing,
    TabuSearch,
    select_method,
)
from app.engines.scoring.scorer import GridScorer, ScoredResult
from app.models.grid import ScoredGrid
from app.models.statistics import StatisticsSnapshot
from app.repositories.grid_repository import GridRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.statistics_repository import StatisticsRepository

logger = structlog.get_logger(__name__)

OPTIMIZER_MAP = {
    "annealing": SimulatedAnnealing,
    "genetic": GeneticAlgorithm,
    "tabu": TabuSearch,
    "hill_climbing": HillClimbing,
}


class GridService:
    """Score grids against the latest statistics snapshot."""

    def __init__(
        self,
        stats_repo: StatisticsRepository,
        grid_repo: GridRepository,
        portfolio_repo: PortfolioRepository | None = None,
    ):
        self._stats_repo = stats_repo
        self._grid_repo = grid_repo
        self._portfolio_repo = portfolio_repo

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
        if snapshot.star_frequencies:
            statistics["star_frequency"] = snapshot.star_frequencies
        if snapshot.star_gaps:
            statistics["star_gaps"] = snapshot.star_gaps

        if custom_weights:
            scorer = GridScorer(weights=custom_weights)
        else:
            scorer = GridScorer.from_profile(profile)

        if stars and game.stars_pool:
            return scorer.score_with_stars(numbers, stars, statistics, game)
        return scorer.score(numbers, statistics, game)

    async def get_top_grids(self, game_id: int, limit: int = 10) -> list[ScoredGrid]:
        """Return the top-scored grids for a game."""
        return await self._grid_repo.get_top_grids(game_id, limit)

    async def get_grid(self, grid_id: int) -> ScoredGrid | None:
        """Return a single grid by ID."""
        return await self._grid_repo.get(grid_id)

    def _build_statistics(self, snapshot: StatisticsSnapshot) -> dict[str, Any]:
        """Build statistics dict from a snapshot."""
        stats = {
            "frequency": snapshot.frequencies,
            "gaps": snapshot.gaps,
            "cooccurrence": snapshot.cooccurrence_matrix,
        }
        if snapshot.star_frequencies:
            stats["star_frequency"] = snapshot.star_frequencies
        if snapshot.star_gaps:
            stats["star_gaps"] = snapshot.star_gaps
        return stats

    async def generate_grids(
        self,
        game_id: int,
        game: GameConfig,
        count: int = 10,
        method: str = "auto",
        profile: str = "equilibre",
        custom_weights: dict[str, float] | None = None,
        seed: int | None = None,
    ) -> tuple[list[ScoredResult], str, float]:
        """Generate optimized grids. Returns (grids, method_used, elapsed_ms)."""
        snapshot = await self._stats_repo.get_latest(game_id)
        if snapshot is None:
            raise InsufficientDataError(
                "No statistics snapshot available. Run statistics computation first."
            )

        statistics = self._build_statistics(snapshot)

        if custom_weights:
            scorer = GridScorer(weights=custom_weights)
        else:
            scorer = GridScorer.from_profile(profile)

        # Resolve method
        if method == "auto":
            method = select_method(game, count)

        optimizer_cls = OPTIMIZER_MAP.get(method)
        if optimizer_cls is None:
            raise ValueError(f"Unknown method '{method}'. Available: {list(OPTIMIZER_MAP.keys())}")

        optimizer = optimizer_cls(
            scorer=scorer,
            statistics=statistics,
            game=game,
            seed=seed,
        )

        start = time.perf_counter()
        results = await asyncio.to_thread(optimizer.optimize, n_grids=count)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "grids_generated",
            method=method,
            count=len(results),
            elapsed_ms=round(elapsed_ms, 1),
        )

        return results, method, elapsed_ms

    async def generate_portfolio(
        self,
        game_id: int,
        game: GameConfig,
        grid_count: int = 10,
        strategy: str = "balanced",
        method: str = "auto",
        profile: str = "equilibre",
        custom_weights: dict[str, float] | None = None,
        seed: int | None = None,
    ) -> tuple[PortfolioResult, str, float]:
        """Generate an optimized portfolio. Returns (portfolio, method_used, elapsed_ms)."""
        # Generate more candidates than needed, then select via portfolio optimizer
        candidate_count = max(grid_count * 5, 50)
        candidates, method_used, gen_ms = await self.generate_grids(
            game_id=game_id,
            game=game,
            count=candidate_count,
            method=method,
            profile=profile,
            custom_weights=custom_weights,
            seed=seed,
        )

        start = time.perf_counter()
        portfolio_optimizer = PortfolioOptimizer(game)
        result = await asyncio.to_thread(
            portfolio_optimizer.optimize, candidates, grid_count, strategy
        )
        portfolio_ms = (time.perf_counter() - start) * 1000

        total_ms = gen_ms + portfolio_ms

        logger.info(
            "portfolio_generated",
            strategy=strategy,
            grid_count=len(result.grids),
            diversity=result.diversity_score,
            coverage=result.coverage_score,
            elapsed_ms=round(total_ms, 1),
        )

        return result, method_used, total_ms

    async def delete_grid(self, grid_id: int) -> bool:
        """Delete a grid by ID. Returns True if deleted."""
        grid = await self._grid_repo.get(grid_id)
        if grid is None:
            return False
        await self._grid_repo.delete(grid)
        return True

    async def toggle_favorite(self, grid_id: int) -> ScoredGrid | None:
        """Toggle is_favorite on a grid. Returns updated grid or None."""
        grid = await self._grid_repo.get(grid_id)
        if grid is None:
            return None
        grid.is_favorite = not grid.is_favorite
        await self._grid_repo.update(grid)
        return grid

    async def toggle_played(self, grid_id: int) -> ScoredGrid | None:
        """Toggle is_played on a grid. Sets played_at when marking as played."""
        grid = await self._grid_repo.get(grid_id)
        if grid is None:
            return None
        grid.is_played = not grid.is_played
        grid.played_at = datetime.now(UTC) if grid.is_played else None
        await self._grid_repo.update(grid)
        return grid

    async def get_favorites(self, game_id: int) -> list[ScoredGrid]:
        """Return all favorite grids for a game."""
        return await self._grid_repo.get_favorites(game_id)

    async def get_played_grids(self, game_id: int) -> list[ScoredGrid]:
        """Return all played grids for a game."""
        return await self._grid_repo.get_played(game_id)

    async def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio by ID. Returns True if deleted."""
        if self._portfolio_repo is None:
            return False
        portfolio = await self._portfolio_repo.get(portfolio_id)
        if portfolio is None:
            return False
        await self._portfolio_repo.delete(portfolio)
        return True
