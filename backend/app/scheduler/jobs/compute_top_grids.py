"""Job: regenerate top grids for all active games."""

from datetime import UTC, datetime

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


async def _do_compute_top_grids() -> dict:
    """Core logic — generate new top grids."""
    configs = load_all_game_configs()
    results = {}

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
                # Mark old top grids as non-top
                old_tops = await grid_repo.get_top_grids(game.id, limit=100)
                for g in old_tops:
                    g.is_top = False
                    await grid_repo.update(g)

                # Generate new optimized grids
                grids, method, elapsed = await grid_service.generate_grids(
                    game_id=game.id,
                    game=config,
                    count=TOP_GRIDS_COUNT,
                    method="auto",
                )

                # Persist as new top grids
                from app.models.grid import ScoredGrid

                for scored in grids:
                    sg = ScoredGrid(
                        game_id=game.id,
                        numbers=scored.numbers,
                        stars=getattr(scored, "stars", None),
                        total_score=scored.total_score,
                        score_breakdown=scored.score_breakdown,
                        method=method,
                        computed_at=datetime.now(UTC),
                        is_top=True,
                    )
                    await grid_repo.create(sg)

                results[game.slug] = {
                    "status": "success",
                    "generated": len(grids),
                    "method": method,
                    "elapsed_ms": round(elapsed, 1),
                }
                logger.info("compute_top_grids.done", slug=game.slug, count=len(grids))

            except Exception as exc:
                results[game.slug] = {"status": "error", "error": str(exc)}
                logger.error("compute_top_grids.failed", slug=game.slug, error=str(exc))

        await session.commit()
        break

    return {"games_processed": len(results), "details": results}
