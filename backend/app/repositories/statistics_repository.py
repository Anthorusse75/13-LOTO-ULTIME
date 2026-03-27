from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.statistics import StatisticsSnapshot

from .base import BaseRepository


class StatisticsRepository(BaseRepository[StatisticsSnapshot]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StatisticsSnapshot)

    async def get_latest(self, game_id: int) -> StatisticsSnapshot | None:
        stmt = (
            select(StatisticsSnapshot)
            .where(StatisticsSnapshot.game_id == game_id)
            .order_by(StatisticsSnapshot.computed_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
