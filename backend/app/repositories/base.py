from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Repository générique avec opérations CRUD de base."""

    def __init__(self, session: AsyncSession, model_class: type[T]):
        self._session = session
        self._model_class = model_class

    async def get(self, id: int) -> T | None:
        return await self._session.get(self._model_class, id)

    async def get_all(self, **filters) -> list[T]:
        stmt = select(self._model_class).filter_by(**filters)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()

    async def count(self, **filters) -> int:
        stmt = select(self._model_class).filter_by(**filters)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
