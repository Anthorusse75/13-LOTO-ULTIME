from datetime import date

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw

from .base import BaseRepository


class DrawRepository(BaseRepository[Draw]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Draw)

    async def get_latest(self, game_id: int, limit: int = 1) -> list[Draw]:
        stmt = (
            select(Draw).where(Draw.game_id == game_id).order_by(Draw.draw_date.desc()).limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_date_range(self, game_id: int, start: date, end: date) -> list[Draw]:
        stmt = (
            select(Draw)
            .where(Draw.game_id == game_id, Draw.draw_date >= start, Draw.draw_date <= end)
            .order_by(Draw.draw_date.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_numbers_matrix(self, game_id: int) -> np.ndarray:
        """Retourne tous les numéros comme matrice NumPy (N tirages × K numéros)."""
        stmt = select(Draw.numbers).where(Draw.game_id == game_id).order_by(Draw.draw_date.asc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        if not rows:
            return np.array([]).reshape(0, 0)
        return np.array(rows)

    async def exists(self, game_id: int, draw_date: date) -> bool:
        stmt = select(Draw.id).where(Draw.game_id == game_id, Draw.draw_date == draw_date)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
