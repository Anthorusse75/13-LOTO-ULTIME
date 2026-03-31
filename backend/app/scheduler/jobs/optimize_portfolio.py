"""Job: regenerate optimized portfolios for all active games."""

from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.game_definitions import load_all_game_configs
from app.models.base import get_session
from app.models.portfolio import Portfolio
from app.repositories.game_repository import GameRepository
from app.repositories.grid_repository import GridRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.scheduler.runner import execute_with_tracking
from app.services.grid import GridService

logger = structlog.get_logger(__name__)

PORTFOLIO_GRID_COUNT = 7
STRATEGIES = ["balanced", "max_diversity", "max_coverage", "min_correlation"]


async def optimize_portfolio_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: regenerate portfolios for all active games."""
    await execute_with_tracking(
        job_name="optimize_portfolio",
        func=_do_optimize_portfolio,
        triggered_by=triggered_by,
    )


async def _do_optimize_portfolio() -> dict[str, Any]:
    """Core logic — generate portfolio per strategy per game."""
    configs = load_all_game_configs()
    results: dict[str, Any] = {}

    # First, get the list of active games (short-lived session)
    async for session in get_session():
        game_repo = GameRepository(session)
        active_games = await game_repo.get_active_games()
        game_data = [(g.id, g.slug) for g in active_games]
        break

    # Process each game×strategy with its own session to avoid holding
    # connections during long CPU-bound grid generation
    for game_id, game_slug in game_data:
        config = configs.get(game_slug)
        if config is None:
            continue

        game_results = {}
        for strategy in STRATEGIES:
            try:
                async for session in get_session():
                    stats_repo = StatisticsRepository(session)
                    grid_repo = GridRepository(session)
                    portfolio_repo = PortfolioRepository(session)
                    grid_service = GridService(stats_repo, grid_repo)

                    portfolio_result, method, elapsed = await grid_service.generate_portfolio(
                        game_id=game_id,
                        game=config,
                        grid_count=PORTFOLIO_GRID_COUNT,
                        strategy=strategy,
                    )

                    grids_data = [
                        {"numbers": g.numbers, "score": g.total_score}
                        for g in portfolio_result.grids
                    ]
                    portfolio = Portfolio(
                        game_id=game_id,
                        name=f"{game_slug}_{strategy}",
                        strategy=strategy,
                        grid_count=len(grids_data),
                        grids=grids_data,
                        diversity_score=portfolio_result.diversity_score,
                        coverage_score=portfolio_result.coverage_score,
                        avg_grid_score=sum(g.total_score for g in portfolio_result.grids)
                        / len(portfolio_result.grids),
                        computed_at=datetime.now(UTC),
                    )
                    await portfolio_repo.create(portfolio)
                    await session.commit()
                    break

                game_results[strategy] = {
                    "status": "success",
                    "grid_count": len(portfolio_result.grids),
                    "diversity": round(portfolio_result.diversity_score, 3),
                    "coverage": round(portfolio_result.coverage_score, 3),
                }

            except Exception as exc:
                game_results[strategy] = {"status": "error", "error": str(exc)}
                logger.error(
                    "optimize_portfolio.failed",
                    slug=game_slug,
                    strategy=strategy,
                    error=str(exc),
                )

        results[game_slug] = game_results

    return {"games_processed": len(results), "details": results}
