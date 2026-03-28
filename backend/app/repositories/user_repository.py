from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_all_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        stmt = select(User).order_by(User.id).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
