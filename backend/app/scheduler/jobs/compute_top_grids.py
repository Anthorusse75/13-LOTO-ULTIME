"""Job: regenerate top grids for all active games."""

from datetime import UTC, datetime
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

TOP_GRIDS_COUNT = 10


async def compute_top_grids_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: regenerate top grids for all active games."""
    await execute_with_tracking(
        job_name="compute_top_grids",
        func=_do_compute_top_grids,
        triggered_by=triggered_by,
    )


async def _do_compute_top_grids() -> dict[str, Any]:
    """Core logic — generate new top grids."""
    configs = load_all_game_configs()
    results: dict[str, Any] = {}

    # First, get the list of active games (short-lived session)
    async for session in get_session():
        game_repo = GameRepository(session)
        active_games = await game_repo.get_active_games()
        # Detach game data we need before closing session
        game_data = [(g.id, g.slug) for g in active_games]
        break

    # Process each game with its own session to avoid holding connections
    # during long CPU-bound grid generation
    for game_id, game_slug in game_data:
        config = configs.get(game_slug)
        if config is None:
            continue

        try:
            async for session in get_session():
                stats_repo = StatisticsRepository(session)
                grid_repo = GridRepository(session)
                grid_service = GridService(stats_repo, grid_repo)

                # Mark old top grids as non-top
                old_tops = await grid_repo.get_top_grids(game_id, limit=100)
                for g in old_tops:
                    g.is_top = False
                    await grid_repo.update(g)

                # Generate new optimized grids (CPU-bound, runs in thread pool)
                grids, method, elapsed = await grid_service.generate_grids(
                    game_id=game_id,
                    game=config,
                    count=TOP_GRIDS_COUNT,
                    method="auto",
                )

                # Persist as new top grids
                from app.models.grid import ScoredGrid

                for scored in grids:
                    sg = ScoredGrid(
                        game_id=game_id,
                        numbers=scored.numbers,
                        stars=getattr(scored, "stars", None),
                        total_score=scored.total_score,
                        score_breakdown=scored.score_breakdown,
                        method=method,
                        computed_at=datetime.now(UTC),
                        is_top=True,
                    )
                    await grid_repo.create(sg)

                await session.commit()
                break

            results[game_slug] = {
                "status": "success",
                "generated": len(grids),
                "method": method,
                "elapsed_ms": round(elapsed, 1),
            }
            logger.info("compute_top_grids.done", slug=game_slug, count=len(grids))

        except Exception as exc:
            results[game_slug] = {"status": "error", "error": str(exc)}
            logger.error("compute_top_grids.failed", slug=game_slug, error=str(exc))

    return {"games_processed": len(results), "details": results}
