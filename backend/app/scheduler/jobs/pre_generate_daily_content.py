"""Job: pre-generate daily content for the dashboard."""

from typing import Any

import structlog

from app.core.game_definitions import load_all_game_configs
from app.models.base import get_session
from app.repositories.game_repository import GameRepository
from app.repositories.grid_repository import GridRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.scheduler.runner import execute_with_tracking
from app.services.grid import GridService

logger = structlog.get_logger(__name__)


async def pre_generate_daily_content_job(triggered_by: str = "scheduler") -> None:
    """Pre-generate content used by the dashboard and stat-of-the-day."""
    await execute_with_tracking(
        job_name="pre_generate_daily_content",
        func=_do_pre_generate,
        triggered_by=triggered_by,
    )


async def _do_pre_generate() -> dict[str, Any]:
    """Generate daily top grids (single grid highlight) for each game."""
    configs = load_all_game_configs()
    results: dict[str, Any] = {}

    async for session in get_session():
        game_repo = GameRepository(session)
        stats_repo = StatisticsRepository(session)
        grid_repo = GridRepository(session)
        grid_service = GridService(stats_repo, grid_repo)

        active_games = await game_repo.get_active_games()

        for game in active_games:
            config = configs.get(game.slug)
            if config is None:
                continue

            try:
                # Generate 1 "daily best" grid using auto method
                scored_results, method_used, elapsed_ms = await grid_service.generate_grids(
                    game_id=game.id,
                    game=config,
                    count=1,
                    method="auto",
                    profile="equilibre",
                )

                best = scored_results[0] if scored_results else None
                results[game.slug] = {
                    "status": "success",
                    "daily_grid": {
                        "numbers": best.numbers if best else [],
                        "score": best.total_score if best else 0,
                        "method": method_used,
                    },
                    "elapsed_ms": round(elapsed_ms, 1),
                }
                logger.info(
                    "daily_content.generated",
                    slug=game.slug,
                    score=best.total_score if best else 0,
                )
            except Exception:
                logger.exception("daily_content.error", slug=game.slug)
                results[game.slug] = {"status": "error"}

    return {"games_processed": len(results), "details": results}
