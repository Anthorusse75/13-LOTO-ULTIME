"""Job: rescore existing grids against latest statistics."""

from typing import Any

import structlog

from app.core.game_definitions import load_all_game_configs
from app.engines.scoring.scorer import GridScorer
from app.models.base import get_session
from app.repositories.game_repository import GameRepository
from app.repositories.grid_repository import GridRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def compute_scoring_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: rescore all grids for active games."""
    await execute_with_tracking(
        job_name="compute_scoring",
        func=_do_compute_scoring,
        triggered_by=triggered_by,
    )


async def _do_compute_scoring() -> dict[str, Any]:
    """Core logic — rescore grids against latest stats snapshot."""
    configs = load_all_game_configs()
    results: dict[str, Any] = {}

    async for session in get_session():
        game_repo = GameRepository(session)
        grid_repo = GridRepository(session)
        stats_repo = StatisticsRepository(session)

        active_games = await game_repo.get_active_games()

        for game in active_games:
            config = configs.get(game.slug)
            if config is None:
                continue

            snapshot = await stats_repo.get_latest(game.id)
            if snapshot is None:
                results[game.slug] = {"status": "skipped", "reason": "no_stats"}
                continue

            statistics = {
                "frequency": snapshot.frequencies,
                "gaps": snapshot.gaps,
                "cooccurrence": snapshot.cooccurrence_matrix,
            }

            grids = await grid_repo.get_all(game_id=game.id)
            scorer = GridScorer.from_profile("equilibre")
            rescored = 0

            for grid in grids:
                try:
                    result = scorer.score(grid.numbers, statistics, config)
                    grid.total_score = result.total_score
                    grid.score_breakdown = result.score_breakdown
                    await grid_repo.update(grid)
                    rescored += 1
                except Exception as exc:
                    logger.warning("compute_scoring.grid_error", grid_id=grid.id, error=str(exc))

            results[game.slug] = {"status": "success", "rescored": rescored}

        await session.commit()
        break

    return {"games_processed": len(results), "details": results}
