from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import GameDefinition

from .base import BaseRepository


class GameRepository(BaseRepository[GameDefinition]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, GameDefinition)

    async def get_by_slug(self, slug: str) -> GameDefinition | None:
        stmt = select(GameDefinition).where(GameDefinition.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_games(self) -> list[GameDefinition]:
        stmt = select(GameDefinition).where(GameDefinition.is_active.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
