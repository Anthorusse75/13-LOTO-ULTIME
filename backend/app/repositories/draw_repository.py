from datetime import date

import numpy as np
from sqlalchemy import func, select
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

    async def count_by_game(self, game_id: int) -> int:
        stmt = select(func.count()).where(Draw.game_id == game_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_paginated(
        self, game_id: int, offset: int = 0, limit: int = 50
    ) -> list[Draw]:
        stmt = (
            select(Draw)
            .where(Draw.game_id == game_id)
            .order_by(Draw.draw_date.desc())
            .offset(offset)
            .limit(limit)
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

    async def get_numbers_matrix(self, game_id: int, last_n: int | None = None) -> np.ndarray:
        """Retourne les numéros comme matrice NumPy (N tirages × K numéros).

        Args:
            last_n: If provided, only return the last N draws (most recent).
        """
        stmt = select(Draw.numbers).where(Draw.game_id == game_id).order_by(Draw.draw_date.desc())
        if last_n is not None:
            stmt = stmt.limit(last_n)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        if not rows:
            return np.array([]).reshape(0, 0)
        # Reverse so oldest first (chronological order)
        return np.array(list(reversed(rows)))

    async def get_stars_matrix(self, game_id: int, last_n: int | None = None) -> np.ndarray:
        """Retourne toutes les étoiles/numéros chance comme matrice NumPy (N × stars_drawn).

        Args:
            last_n: If provided, only return the last N draws (most recent).
        """
        stmt = (
            select(Draw.stars)
            .where(Draw.game_id == game_id, Draw.stars.isnot(None))
            .order_by(Draw.draw_date.desc())
        )
        if last_n is not None:
            stmt = stmt.limit(last_n)
        result = await self._session.execute(stmt)
        rows = [r for r in result.scalars().all() if r]
        if not rows:
            return np.array([]).reshape(0, 0)
        # Reverse so oldest first (chronological order)
        return np.array(list(reversed(rows)))

    async def exists(self, game_id: int, draw_date: date) -> bool:
        stmt = select(Draw.id).where(Draw.game_id == game_id, Draw.draw_date == draw_date)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
