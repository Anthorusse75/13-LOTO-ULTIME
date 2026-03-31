"""Job: clean up old notifications."""

from typing import Any

import structlog
from sqlalchemy import select

from app.models.base import get_session
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.scheduler.runner import execute_with_tracking
from app.services.notification import NotificationService

logger = structlog.get_logger(__name__)


async def cleanup_notifications_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: clean up old notifications for all users."""
    await execute_with_tracking(
        job_name="cleanup_notifications",
        func=_do_cleanup_notifications,
        triggered_by=triggered_by,
    )


async def _do_cleanup_notifications() -> dict[str, Any]:
    """Core logic — keep only the 100 most recent notifications per user."""
    cleaned = 0

    async for session in get_session():
        stmt = select(User.id)
        result = await session.execute(stmt)
        user_ids = list(result.scalars().all())

        notif_repo = NotificationRepository(session)
        notif_service = NotificationService(notif_repo)

        for user_id in user_ids:
            try:
                count = await notif_service.cleanup(user_id, keep=100)
                cleaned += count
            except Exception as exc:
                logger.error(
                    "cleanup_notifications.failed",
                    user_id=user_id,
                    error=str(exc),
                )

        await session.commit()
        break

    return {"cleaned": cleaned, "users_processed": len(user_ids)}
