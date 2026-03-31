"""Repository for UserNotification persistence."""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import UserNotification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[UserNotification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserNotification)

    async def get_by_user(
        self,
        user_id: int,
        *,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[UserNotification]:
        stmt = (
            select(UserNotification)
            .where(UserNotification.user_id == user_id)
        )
        if unread_only:
            stmt = stmt.where(UserNotification.is_read == False)  # noqa: E712
        stmt = (
            stmt.order_by(UserNotification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(UserNotification)
            .where(
                UserNotification.user_id == user_id,
                UserNotification.is_read == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def mark_read(self, notification_id: int, user_id: int) -> bool:
        stmt = (
            update(UserNotification)
            .where(
                UserNotification.id == notification_id,
                UserNotification.user_id == user_id,
            )
            .values(is_read=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def mark_all_read(self, user_id: int) -> int:
        stmt = (
            update(UserNotification)
            .where(
                UserNotification.user_id == user_id,
                UserNotification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def cleanup_old(self, user_id: int, *, keep: int = 100) -> int:
        """Keep only the most recent `keep` notifications per user."""
        # Get the ID threshold
        stmt = (
            select(UserNotification.id)
            .where(UserNotification.user_id == user_id)
            .order_by(UserNotification.created_at.desc())
            .offset(keep)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        threshold_id = result.scalar_one_or_none()
        if threshold_id is None:
            return 0

        from sqlalchemy import delete as sa_delete

        del_stmt = (
            sa_delete(UserNotification)
            .where(
                UserNotification.user_id == user_id,
                UserNotification.id <= threshold_id,
            )
        )
        result = await self._session.execute(del_stmt)
        return result.rowcount
