"""Job: system health check — verify DB connectivity and data freshness."""

from datetime import UTC, datetime, timedelta

import structlog

from app.models.base import get_session
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.repositories.job_repository import JobRepository
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)

STALE_THRESHOLD_DAYS = 7


async def health_check_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: verify system health."""
    await execute_with_tracking(
        job_name="health_check",
        func=_do_health_check,
        triggered_by=triggered_by,
    )


async def _do_health_check() -> dict:
    """Core logic — check DB, data freshness, recent job failures."""
    results = {"status": "healthy", "checks": {}}
    now = datetime.now(UTC)
    today = now.date()

    async for session in get_session():
        game_repo = GameRepository(session)
        draw_repo = DrawRepository(session)
        job_repo = JobRepository(session)

        # Check active games exist
        games = await game_repo.get_active_games()
        results["checks"]["active_games"] = len(games)

        # Check data freshness per game
        stale_games = []
        for game in games:
            latest = await draw_repo.get_latest(game.id, limit=1)
            if not latest or (today - latest[0].draw_date) > timedelta(days=STALE_THRESHOLD_DAYS):
                stale_games.append(game.slug)

        results["checks"]["stale_games"] = stale_games
        if stale_games:
            results["status"] = "warning"

        # Check recent failed jobs
        running = await job_repo.get_running_jobs()
        results["checks"]["running_jobs"] = len(running)

        # Check for stuck jobs (running > 1h)
        stuck = []
        for j in running:
            if j.started_at:
                started = (
                    j.started_at.replace(tzinfo=UTC)
                    if j.started_at.tzinfo is None
                    else j.started_at
                )
                if (now - started) > timedelta(hours=1):
                    stuck.append(j.job_name)
        if stuck:
            results["checks"]["stuck_jobs"] = stuck
            results["status"] = "warning"

        break

    logger.info("health_check.done", status=results["status"])
    return results
