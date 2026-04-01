"""Job: cleanup anonymous/orphaned data (grids/portfolios without user_id, old temp data)."""

from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import and_, delete

from app.models.base import get_session
from app.models.grid import ScoredGrid
from app.models.portfolio import Portfolio
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)

# Anonymous data older than 7 days is considered abandoned
RETENTION_DAYS_ANONYMOUS = 7


async def cleanup_anonymous_data_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: cleanup anonymous/orphaned data."""
    await execute_with_tracking(
        job_name="cleanup_anonymous_data",
        func=_do_cleanup_anonymous,
        triggered_by=triggered_by,
    )


async def _do_cleanup_anonymous() -> dict[str, Any]:
    """Delete grids and portfolios with no user_id older than retention period."""
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=RETENTION_DAYS_ANONYMOUS)
    results: dict[str, Any] = {}

    async for session in get_session():
        # Clean anonymous grids (no user_id, older than cutoff)
        stmt_grids = delete(ScoredGrid).where(
            and_(
                ScoredGrid.user_id.is_(None),
                ScoredGrid.computed_at < cutoff,
            )
        )
        result = await session.execute(stmt_grids)
        results["anonymous_grids_deleted"] = result.rowcount  # type: ignore[attr-defined]

        # Clean anonymous portfolios (no user_id, older than cutoff)
        stmt_portfolios = delete(Portfolio).where(
            and_(
                Portfolio.user_id.is_(None),
                Portfolio.created_at < cutoff,
            )
        )
        result = await session.execute(stmt_portfolios)
        results["anonymous_portfolios_deleted"] = result.rowcount  # type: ignore[attr-defined]

        await session.commit()

    logger.info("cleanup_anonymous_data_completed", **results)
    return results
