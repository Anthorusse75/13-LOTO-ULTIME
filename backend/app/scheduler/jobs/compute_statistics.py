"""Job: recompute statistics for all active games."""

import structlog

from app.core.game_definitions import load_all_game_configs
from app.models.base import get_session
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.scheduler.runner import execute_with_tracking
from app.services.statistics import StatisticsService

logger = structlog.get_logger(__name__)


async def compute_stats_job() -> None:
    """Scheduled job: recompute statistics for all active games."""
    await execute_with_tracking(
        job_name="compute_stats",
        func=_do_compute_stats,
        triggered_by="scheduler",
    )


async def _do_compute_stats() -> dict:
    """Core logic — compute stats for every active game."""
    configs = load_all_game_configs()
    results = {}

    async for session in get_session():
        game_repo = GameRepository(session)
        draw_repo = DrawRepository(session)
        stats_repo = StatisticsRepository(session)
        stats_service = StatisticsService(draw_repo, stats_repo)

        active_games = await game_repo.get_active_games()

        for game in active_games:
            config = configs.get(game.slug)
            if config is None:
                logger.warning("compute_stats.no_config", slug=game.slug)
                continue

            try:
                snapshot = await stats_service.compute_all(game.id, config)
                results[game.slug] = {
                    "status": "success",
                    "snapshot_id": snapshot.id,
                    "draw_count": snapshot.draw_count,
                }
                logger.info(
                    "compute_stats.game_done",
                    slug=game.slug,
                    snapshot_id=snapshot.id,
                )
            except Exception as exc:
                results[game.slug] = {"status": "error", "error": str(exc)}
                logger.error("compute_stats.game_failed", slug=game.slug, error=str(exc))

        await session.commit()
        break

    return {"games_processed": len(results), "details": results}
