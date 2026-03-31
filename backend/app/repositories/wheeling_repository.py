"""Repository for WheelingSystem persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wheeling import WheelingSystem
from app.repositories.base import BaseRepository


class WheelingRepository(BaseRepository[WheelingSystem]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WheelingSystem)

    async def get_by_user(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> list[WheelingSystem]:
        stmt = (
            select(WheelingSystem)
            .where(WheelingSystem.user_id == user_id)
            .order_by(WheelingSystem.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_game(
        self, user_id: int, game_id: int, *, limit: int = 50
    ) -> list[WheelingSystem]:
        stmt = (
            select(WheelingSystem)
            .where(WheelingSystem.user_id == user_id, WheelingSystem.game_id == game_id)
            .order_by(WheelingSystem.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
