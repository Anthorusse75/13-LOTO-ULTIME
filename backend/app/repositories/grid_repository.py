from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grid import ScoredGrid

from .base import BaseRepository


class GridRepository(BaseRepository[ScoredGrid]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ScoredGrid)

    async def get_top_grids(self, game_id: int, limit: int = 10) -> list[ScoredGrid]:
        stmt = (
            select(ScoredGrid)
            .where(ScoredGrid.game_id == game_id, ScoredGrid.is_top.is_(True))
            .order_by(ScoredGrid.total_score.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_method(self, game_id: int, method: str) -> list[ScoredGrid]:
        stmt = (
            select(ScoredGrid)
            .where(ScoredGrid.game_id == game_id, ScoredGrid.method == method)
            .order_by(ScoredGrid.total_score.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_favorites(self, game_id: int) -> list[ScoredGrid]:
        stmt = (
            select(ScoredGrid)
            .where(ScoredGrid.game_id == game_id, ScoredGrid.is_favorite.is_(True))
            .order_by(ScoredGrid.total_score.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
