"""Repository for BudgetPlan persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import BudgetPlan
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[BudgetPlan]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BudgetPlan)

    async def get_by_user_and_game(
        self, user_id: int, game_id: int, *, limit: int = 50
    ) -> list[BudgetPlan]:
        stmt = (
            select(BudgetPlan)
            .where(BudgetPlan.user_id == user_id, BudgetPlan.game_id == game_id)
            .order_by(BudgetPlan.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
