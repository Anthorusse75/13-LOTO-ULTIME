"""Job: compute hot/cold summary for the dashboard."""

from typing import Any

import structlog

from app.core.game_definitions import load_all_game_configs
from app.models.base import get_session
from app.repositories.game_repository import GameRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def compute_hot_cold_job(triggered_by: str = "scheduler") -> None:
    """Compute hot/cold number summary and persist in latest snapshot."""
    await execute_with_tracking(
        job_name="compute_hot_cold",
        func=_do_compute_hot_cold,
        triggered_by=triggered_by,
    )


async def _do_compute_hot_cold() -> dict[str, Any]:
    """Extract hot/cold numbers from latest statistics snapshot."""
    results: dict[str, Any] = {}

    async for session in get_session():
        game_repo = GameRepository(session)
        stats_repo = StatisticsRepository(session)

        active_games = await game_repo.get_active_games()

        for game in active_games:
            snapshot = await stats_repo.get_latest(game.id)
            if not snapshot or not snapshot.frequencies:
                logger.warning("hot_cold.no_snapshot", slug=game.slug)
                continue

            freqs: list[dict[str, Any]] = snapshot.frequencies
            if not freqs:
                continue

            # Sort by relative frequency (descending)
            sorted_by_freq = sorted(freqs, key=lambda f: f.get("relative", 0), reverse=True)

            hot_numbers = [f["number"] for f in sorted_by_freq[:10]]
            cold_numbers = [f["number"] for f in sorted_by_freq[-10:]]

            # Build summary
            summary = {
                "hot_numbers": hot_numbers,
                "cold_numbers": cold_numbers,
                "hottest": sorted_by_freq[0] if sorted_by_freq else None,
                "coldest": sorted_by_freq[-1] if sorted_by_freq else None,
                "total_draws": snapshot.draw_count,
            }

            # Persist on the snapshot
            snapshot.hot_cold_summary = summary
            session.add(snapshot)
            await session.commit()

            results[game.slug] = {
                "status": "success",
                "hot": hot_numbers[:5],
                "cold": cold_numbers[:5],
            }
            logger.info("hot_cold.computed", slug=game.slug, hot=hot_numbers[:5])

    return {"games_processed": len(results), "details": results}
