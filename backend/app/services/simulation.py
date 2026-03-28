"""Simulation service — orchestrates Monte Carlo and robustness analysis."""

import time

import structlog

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer
from app.engines.simulation import (
    ComparisonResult,
    MonteCarloSimulator,
    PortfolioSimulationResult,
    RobustnessAnalyzer,
    SimulationResult,
    StabilityResult,
)
from app.repositories.draw_repository import DrawRepository
from app.repositories.statistics_repository import StatisticsRepository

logger = structlog.get_logger(__name__)

MIN_DRAWS_FOR_BOOTSTRAP = 30


class SimulationService:
    """Orchestrate simulation engines with data access."""

    def __init__(
        self,
        draw_repo: DrawRepository,
        stats_repo: StatisticsRepository,
    ):
        self._draw_repo = draw_repo
        self._stats_repo = stats_repo

    async def simulate_grid(
        self,
        game_id: int,
        game: GameConfig,
        grid: list[int],
        stars: list[int] | None = None,
        n_simulations: int = 10_000,
        seed: int | None = None,
    ) -> tuple[SimulationResult, float]:
        """Run Monte Carlo simulation on a single grid. Returns (result, elapsed_ms)."""
        simulator = MonteCarloSimulator(game=game, seed=seed)
        start = time.perf_counter()
        result = simulator.simulate_grid(grid, stars, n_simulations)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "monte_carlo_grid",
            game_id=game_id,
            n_simulations=n_simulations,
            avg_matches=result.avg_matches,
            elapsed_ms=round(elapsed_ms, 1),
        )

        return result, elapsed_ms

    async def simulate_portfolio(
        self,
        game_id: int,
        game: GameConfig,
        portfolio: list[list[int]],
        n_simulations: int = 10_000,
        min_matches: int = 2,
        seed: int | None = None,
    ) -> tuple[PortfolioSimulationResult, float]:
        """Run Monte Carlo simulation on a portfolio. Returns (result, elapsed_ms)."""
        simulator = MonteCarloSimulator(game=game, seed=seed)
        start = time.perf_counter()
        result = simulator.simulate_portfolio(portfolio, n_simulations, min_matches)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "monte_carlo_portfolio",
            game_id=game_id,
            n_grids=len(portfolio),
            n_simulations=n_simulations,
            hit_rate=result.hit_rate,
            elapsed_ms=round(elapsed_ms, 1),
        )

        return result, elapsed_ms

    async def analyze_stability(
        self,
        game_id: int,
        game: GameConfig,
        grid: list[int],
        n_bootstrap: int = 100,
        profile: str = "equilibre",
        seed: int | None = None,
    ) -> tuple[StabilityResult, float]:
        """Bootstrap stability analysis. Returns (result, elapsed_ms)."""
        draws = await self._draw_repo.get_numbers_matrix(game_id)
        if draws.shape[0] < MIN_DRAWS_FOR_BOOTSTRAP:
            raise InsufficientDataError(
                f"Need at least {MIN_DRAWS_FOR_BOOTSTRAP} draws for bootstrap, "
                f"got {draws.shape[0]}"
            )

        scorer = GridScorer.from_profile(profile)
        analyzer = RobustnessAnalyzer(seed=seed)

        start = time.perf_counter()
        result = analyzer.analyze_stability(grid, draws, game, scorer, n_bootstrap)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "stability_analysis",
            game_id=game_id,
            stability=result.stability,
            mean_score=result.mean_score,
            elapsed_ms=round(elapsed_ms, 1),
        )

        return result, elapsed_ms

    async def compare_with_random(
        self,
        game_id: int,
        game: GameConfig,
        grid: list[int],
        n_random: int = 1000,
        profile: str = "equilibre",
        seed: int | None = None,
    ) -> tuple[ComparisonResult, float]:
        """Compare grid score against random grids. Returns (result, elapsed_ms)."""
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

        scorer = GridScorer.from_profile(profile)
        grid_result = scorer.score(grid, statistics, game)
        analyzer = RobustnessAnalyzer(seed=seed)

        start = time.perf_counter()
        result = analyzer.compare_with_random(
            grid_score=grid_result.total_score,
            game=game,
            statistics=statistics,
            scorer=scorer,
            n_random=n_random,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "random_comparison",
            game_id=game_id,
            percentile=result.percentile,
            z_score=result.z_score,
            elapsed_ms=round(elapsed_ms, 1),
        )

        return result, elapsed_ms
