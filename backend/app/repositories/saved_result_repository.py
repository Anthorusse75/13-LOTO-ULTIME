"""Repository for user saved results."""

from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_result import UserSavedResult


class SavedResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, result: UserSavedResult) -> UserSavedResult:
        self.session.add(result)
        await self.session.flush()
        return result

    async def get(self, result_id: int) -> UserSavedResult | None:
        return await self.session.get(UserSavedResult, result_id)

    async def get_by_user(self, result_id: int, user_id: int) -> UserSavedResult | None:
        stmt = select(UserSavedResult).where(
            UserSavedResult.id == result_id,
            UserSavedResult.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_user(
        self,
        user_id: int,
        result_type: str | None = None,
        is_favorite: bool | None = None,
    ) -> int:
        stmt = select(func.count(UserSavedResult.id)).where(
            UserSavedResult.user_id == user_id
        )
        if result_type:
            stmt = stmt.where(UserSavedResult.result_type == result_type)
        if is_favorite is not None:
            stmt = stmt.where(UserSavedResult.is_favorite == is_favorite)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def list_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 50,
        result_type: str | None = None,
        is_favorite: bool | None = None,
    ) -> list[UserSavedResult]:
        stmt = (
            select(UserSavedResult)
            .where(UserSavedResult.user_id == user_id)
            .order_by(UserSavedResult.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if result_type:
            stmt = stmt.where(UserSavedResult.result_type == result_type)
        if is_favorite is not None:
            stmt = stmt.where(UserSavedResult.is_favorite == is_favorite)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, result_id: int, user_id: int) -> bool:
        stmt = delete(UserSavedResult).where(
            UserSavedResult.id == result_id,
            UserSavedResult.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def update_favorite(self, result_id: int, user_id: int, is_favorite: bool) -> bool:
        stmt = (
            update(UserSavedResult)
            .where(UserSavedResult.id == result_id, UserSavedResult.user_id == user_id)
            .values(is_favorite=is_favorite)
        )
        result = await self.session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def update_tags(self, result_id: int, user_id: int, tags: list[str]) -> bool:
        stmt = (
            update(UserSavedResult)
            .where(UserSavedResult.id == result_id, UserSavedResult.user_id == user_id)
            .values(tags=tags)
        )
        result = await self.session.execute(stmt)
        return (result.rowcount or 0) > 0
