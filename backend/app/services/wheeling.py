"""Wheeling service — preview, generate, persist, and retrieve wheeling systems."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_definitions import GameConfig
from app.engines.wheeling.engine import WheelingEngine, WheelingResult
from app.models.prize_tier import GamePrizeTier
from app.models.wheeling import WheelingSystem
from app.repositories.wheeling_repository import WheelingRepository
from app.schemas.wheeling import WheelingPreviewResponse

logger = structlog.get_logger(__name__)


class WheelingService:
    def __init__(self, repo: WheelingRepository, session: AsyncSession):
        self._repo = repo
        self._session = session

    async def preview(
        self,
        game_config: GameConfig,
        numbers: list[int],
        stars: list[int] | None,
        guarantee: int,
    ) -> WheelingPreviewResponse:
        engine = WheelingEngine(game_config)
        result = engine.preview(numbers, stars, guarantee)
        return WheelingPreviewResponse(
            estimated_grid_count=result.estimated_grid_count,
            estimated_cost=result.estimated_cost,
            total_t_combinations=result.total_t_combinations,
            full_wheel_size=result.full_wheel_size,
            reduction_rate_estimate=result.reduction_rate_estimate,
        )

    async def generate(
        self,
        game_id: int,
        game_config: GameConfig,
        user_id: int,
        numbers: list[int],
        stars: list[int] | None,
        guarantee: int,
    ) -> tuple[WheelingResult, WheelingSystem]:
        # Fetch prize tiers for gain analysis
        prize_tiers = await self._get_prize_tiers(game_id)

        engine = WheelingEngine(game_config)
        result = engine.generate(numbers, stars, guarantee, prize_tiers=prize_tiers)

        # Persist
        system = WheelingSystem(
            user_id=user_id,
            game_id=game_id,
            selected_numbers=numbers,
            selected_stars=stars,
            guarantee_level=guarantee,
            grids=[{"numbers": g.numbers, "stars": g.stars} for g in result.grids],
            grid_count=result.grid_count,
            total_cost=result.total_cost,
            coverage_rate=result.coverage_rate,
            reduction_rate=result.reduction_rate,
        )
        system = await self._repo.create(system)

        return result, system

    async def get_user_systems(
        self, user_id: int, game_id: int, *, limit: int = 50
    ) -> list[WheelingSystem]:
        return await self._repo.get_by_user_and_game(user_id, game_id, limit=limit)

    async def get_system(self, system_id: int) -> WheelingSystem | None:
        return await self._repo.get(system_id)

    async def delete_system(self, system_id: int, user_id: int) -> bool:
        system = await self._repo.get(system_id)
        if system is None or system.user_id != user_id:
            return False
        await self._repo.delete(system)
        return True

    async def _get_prize_tiers(self, game_id: int) -> list[dict[str, Any]]:
        stmt = select(GamePrizeTier).where(GamePrizeTier.game_id == game_id)
        result = await self._session.execute(stmt)
        tiers = result.scalars().all()
        return [
            {
                "rank": t.rank,
                "name": t.name,
                "match_numbers": t.match_numbers,
                "match_stars": t.match_stars,
                "avg_prize": t.avg_prize,
                "probability": t.probability,
            }
            for t in tiers
        ]
