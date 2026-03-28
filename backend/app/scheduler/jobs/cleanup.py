"""Job: cleanup old data (snapshots, job history, old grids)."""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import delete

from app.models.base import get_session
from app.models.job import JobExecution
from app.models.statistics import StatisticsSnapshot
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)

RETENTION_DAYS_JOBS = 90
RETENTION_DAYS_SNAPSHOTS = 30
MAX_SNAPSHOTS_PER_GAME = 10


async def cleanup_job() -> None:
    """Scheduled job: cleanup old data."""
    await execute_with_tracking(
        job_name="cleanup",
        func=_do_cleanup,
        triggered_by="scheduler",
    )


async def _do_cleanup() -> dict:
    """Core logic — delete old job records and old snapshots."""
    now = datetime.now(UTC)
    results = {}

    async for session in get_session():
        # Clean old job executions
        cutoff_jobs = now - timedelta(days=RETENTION_DAYS_JOBS)
        stmt = delete(JobExecution).where(JobExecution.started_at < cutoff_jobs)
        result = await session.execute(stmt)
        results["jobs_deleted"] = result.rowcount

        # Clean old statistics snapshots
        cutoff_stats = now - timedelta(days=RETENTION_DAYS_SNAPSHOTS)
        stmt = delete(StatisticsSnapshot).where(StatisticsSnapshot.computed_at < cutoff_stats)
        result = await session.execute(stmt)
        results["snapshots_deleted"] = result.rowcount

        await session.commit()
        break

    logger.info("cleanup.done", **results)
    return results
