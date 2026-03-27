from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio

from .base import BaseRepository


class PortfolioRepository(BaseRepository[Portfolio]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Portfolio)

    async def get_latest(self, game_id: int) -> Portfolio | None:
        stmt = (
            select(Portfolio)
            .where(Portfolio.game_id == game_id)
            .order_by(Portfolio.computed_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_strategy(self, game_id: int, strategy: str) -> list[Portfolio]:
        stmt = (
            select(Portfolio)
            .where(Portfolio.game_id == game_id, Portfolio.strategy == strategy)
            .order_by(Portfolio.computed_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
