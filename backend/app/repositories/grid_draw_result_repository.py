"""Repository for GridDrawResult persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grid_draw_result import GridDrawResult
from app.repositories.base import BaseRepository


class GridDrawResultRepository(BaseRepository[GridDrawResult]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, GridDrawResult)

    async def get_by_grid(self, scored_grid_id: int) -> list[GridDrawResult]:
        stmt = (
            select(GridDrawResult)
            .where(GridDrawResult.scored_grid_id == scored_grid_id)
            .order_by(GridDrawResult.checked_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_draw(self, draw_id: int) -> list[GridDrawResult]:
        stmt = (
            select(GridDrawResult)
            .where(GridDrawResult.draw_id == draw_id)
            .order_by(GridDrawResult.match_count.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, scored_grid_id: int, draw_id: int) -> bool:
        stmt = select(GridDrawResult.id).where(
            GridDrawResult.scored_grid_id == scored_grid_id,
            GridDrawResult.draw_id == draw_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_recent_results(
        self, user_grid_ids: list[int], *, limit: int = 50
    ) -> list[GridDrawResult]:
        if not user_grid_ids:
            return []
        stmt = (
            select(GridDrawResult)
            .where(GridDrawResult.scored_grid_id.in_(user_grid_ids))
            .order_by(GridDrawResult.checked_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
