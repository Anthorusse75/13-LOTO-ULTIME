"""Job: check played grids against latest draws."""

from typing import Any

import structlog

from app.models.base import get_session
from app.repositories.game_repository import GameRepository
from app.scheduler.runner import execute_with_tracking
from app.services.automation import AutomationService

logger = structlog.get_logger(__name__)


async def check_played_grids_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: check all played grids against latest draws."""
    await execute_with_tracking(
        job_name="check_played_grids",
        func=_do_check_played_grids,
        triggered_by=triggered_by,
    )


async def _do_check_played_grids() -> dict[str, Any]:
    """Core logic — check played grids for each active game."""
    results: dict[str, Any] = {}

    async for session in get_session():
        game_repo = GameRepository(session)
        active_games = await game_repo.get_active_games()
        game_data = [(g.id, g.slug) for g in active_games]
        break

    for game_id, game_slug in game_data:
        try:
            async for session in get_session():
                automation = AutomationService(session)
                grid_results = await automation.check_played_grids(game_id)
                await session.commit()
                break

            results[game_slug] = {
                "status": "success",
                "checked": len(grid_results),
                "winners": sum(1 for r in grid_results if r.prize_rank is not None),
            }
            logger.info(
                "check_played_grids.done",
                slug=game_slug,
                checked=len(grid_results),
            )
        except Exception as exc:
            results[game_slug] = {"status": "error", "error": str(exc)}
            logger.error(
                "check_played_grids.failed", slug=game_slug, error=str(exc)
            )

    return {"games_processed": len(results), "details": results}
