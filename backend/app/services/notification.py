"""Notification service — create and manage user notifications."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from app.models.notification import UserNotification
from app.repositories.notification_repository import NotificationRepository

logger = structlog.get_logger(__name__)


class NotificationService:
    """Create and query user notifications."""

    def __init__(self, notification_repo: NotificationRepository):
        self._repo = notification_repo

    async def get_notifications(
        self,
        user_id: int,
        *,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
    ) -> tuple[list[UserNotification], int]:
        """Get paginated notifications for a user."""
        notifications = await self._repo.get_by_user(
            user_id, limit=limit, offset=offset, unread_only=unread_only
        )
        unread_count = await self._repo.get_unread_count(user_id)
        return notifications, unread_count

    async def get_unread_count(self, user_id: int) -> int:
        return await self._repo.get_unread_count(user_id)

    async def mark_read(self, notification_id: int, user_id: int) -> bool:
        return await self._repo.mark_read(notification_id)

    async def mark_all_read(self, user_id: int) -> int:
        return await self._repo.mark_all_read(user_id)

    async def create_notification(
        self,
        user_id: int,
        *,
        notification_type: str,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> UserNotification:
        """Create a single notification."""
        notif = UserNotification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            is_read=False,
            created_at=datetime.now(UTC),
        )
        return await self._repo.create(notif)

    async def notify_grid_result(
        self,
        user_id: int,
        grid_id: int,
        match_count: int,
        star_match_count: int,
        prize_rank: int | None,
        estimated_prize: float,
    ) -> UserNotification:
        """Create a notification for grid result checking."""
        if prize_rank:
            title = f"🎉 Rang {prize_rank} — {estimated_prize:.2f}€ !"
            message = (
                f"Votre grille a {match_count} numéro(s) et "
                f"{star_match_count} étoile(s) en commun avec le tirage."
            )
        else:
            title = "Résultat de votre grille"
            message = (
                f"Votre grille a {match_count} numéro(s) et "
                f"{star_match_count} étoile(s) en commun avec le tirage."
            )

        return await self.create_notification(
            user_id,
            notification_type="grid_result",
            title=title,
            message=message,
            data={
                "grid_id": grid_id,
                "match_count": match_count,
                "star_match_count": star_match_count,
                "prize_rank": prize_rank,
                "estimated_prize": estimated_prize,
            },
        )

    async def notify_new_draw(
        self, user_id: int, game_name: str, draw_date: str
    ) -> UserNotification:
        """Notify a user about a new draw."""
        return await self.create_notification(
            user_id,
            notification_type="new_draw",
            title=f"Nouveau tirage {game_name}",
            message=f"Le tirage du {draw_date} est disponible. Consultez les résultats !",
            data={"game_name": game_name, "draw_date": draw_date},
        )

    async def cleanup(self, user_id: int, *, keep: int = 100) -> int:
        """Clean up old notifications, keeping the most recent ones."""
        return await self._repo.cleanup_old(user_id, keep=keep)
