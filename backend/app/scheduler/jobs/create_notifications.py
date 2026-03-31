"""Job: create notifications for grid draw results."""

from typing import Any

import structlog

from app.models.base import get_session
from app.models.grid import ScoredGrid
from app.models.grid_draw_result import GridDrawResult
from app.repositories.game_repository import GameRepository
from app.repositories.grid_draw_result_repository import GridDrawResultRepository
from app.repositories.notification_repository import NotificationRepository
from app.scheduler.runner import execute_with_tracking
from app.services.notification import NotificationService

logger = structlog.get_logger(__name__)


async def create_grid_result_notifications_job(
    triggered_by: str = "scheduler",
) -> None:
    """Scheduled job: notify users about their grid results."""
    await execute_with_tracking(
        job_name="create_grid_result_notifications",
        func=_do_create_grid_result_notifications,
        triggered_by=triggered_by,
    )


async def _do_create_grid_result_notifications() -> dict[str, Any]:
    """Core logic — create notifications for recent grid results."""
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    notified = 0
    errors = 0

    async for session in get_session():
        game_repo = GameRepository(session)
        active_games = await game_repo.get_active_games()
        game_ids = [g.id for g in active_games]

        result_repo = GridDrawResultRepository(session)
        notif_repo = NotificationRepository(session)
        notif_service = NotificationService(notif_repo)

        for game_id in game_ids:
            # Get recent unchecked results (last 24h via checked_at)
            from datetime import UTC, datetime, timedelta

            stmt = (
                select(GridDrawResult)
                .join(ScoredGrid, GridDrawResult.scored_grid_id == ScoredGrid.id)
                .where(
                    ScoredGrid.game_id == game_id,
                    ScoredGrid.user_id.isnot(None),
                    GridDrawResult.checked_at >= datetime.now(UTC) - timedelta(hours=24),
                )
            )
            result = await session.execute(stmt)
            recent_results = list(result.scalars().all())

            for grid_result in recent_results:
                try:
                    # Get grid to find user_id
                    grid_stmt = select(ScoredGrid).where(
                        ScoredGrid.id == grid_result.scored_grid_id
                    )
                    grid_r = await session.execute(grid_stmt)
                    grid = grid_r.scalar_one_or_none()

                    if grid and grid.user_id:
                        await notif_service.notify_grid_result(
                            user_id=grid.user_id,
                            grid_id=grid.id,
                            match_count=grid_result.match_count,
                            star_match_count=grid_result.star_match_count,
                            prize_rank=grid_result.prize_rank,
                            estimated_prize=grid_result.estimated_prize or 0.0,
                        )
                        notified += 1
                except Exception as exc:
                    errors += 1
                    logger.error(
                        "grid_result_notification.failed",
                        grid_result_id=grid_result.id,
                        error=str(exc),
                    )

        await session.commit()
        break

    return {"notified": notified, "errors": errors}
