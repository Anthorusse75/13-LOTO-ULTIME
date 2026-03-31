"""Job: cleanup old data (snapshots, job history, old grids, old portfolios)."""

from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import delete

from app.models.base import get_session
from app.models.grid import ScoredGrid
from app.models.job import JobExecution
from app.models.portfolio import Portfolio
from app.models.statistics import StatisticsSnapshot
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)

RETENTION_DAYS_JOBS = 90
RETENTION_DAYS_SNAPSHOTS = 30
RETENTION_DAYS_GRIDS = 30
RETENTION_DAYS_PORTFOLIOS = 30
MAX_SNAPSHOTS_PER_GAME = 10


async def cleanup_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: cleanup old data."""
    await execute_with_tracking(
        job_name="cleanup",
        func=_do_cleanup,
        triggered_by=triggered_by,
    )


async def _do_cleanup() -> dict[str, Any]:
    """Core logic — delete old job records, old snapshots, old grids, old portfolios."""
    now = datetime.now(UTC)
    results: dict[str, Any] = {}

    async for session in get_session():
        # Clean old job executions
        cutoff_jobs = now - timedelta(days=RETENTION_DAYS_JOBS)
        stmt = delete(JobExecution).where(JobExecution.started_at < cutoff_jobs)
        result = await session.execute(stmt)
        results["jobs_deleted"] = result.rowcount  # type: ignore[attr-defined]

        # Clean old statistics snapshots
        cutoff_stats = now - timedelta(days=RETENTION_DAYS_SNAPSHOTS)
        stmt = delete(StatisticsSnapshot).where(StatisticsSnapshot.computed_at < cutoff_stats)
        result = await session.execute(stmt)
        results["snapshots_deleted"] = result.rowcount  # type: ignore[attr-defined]

        # Clean old scored grids (non-top, older than 30 days)
        cutoff_grids = now - timedelta(days=RETENTION_DAYS_GRIDS)
        stmt = delete(ScoredGrid).where(
            ScoredGrid.computed_at < cutoff_grids,
            ScoredGrid.is_top == False,  # noqa: E712
        )
        result = await session.execute(stmt)
        results["grids_deleted"] = result.rowcount  # type: ignore[attr-defined]

        # Clean old portfolios
        cutoff_portfolios = now - timedelta(days=RETENTION_DAYS_PORTFOLIOS)
        stmt = delete(Portfolio).where(Portfolio.computed_at < cutoff_portfolios)
        result = await session.execute(stmt)
        results["portfolios_deleted"] = result.rowcount  # type: ignore[attr-defined]

        await session.commit()
        break

    logger.info("cleanup.done", **results)
    return results
