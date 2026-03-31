"""Automation service — check played grids against draws, determine prizes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.models.grid import ScoredGrid
from app.models.grid_draw_result import GridDrawResult
from app.models.prize_tier import GamePrizeTier
from app.repositories.grid_draw_result_repository import GridDrawResultRepository

logger = structlog.get_logger(__name__)


def compare_grid_to_draw(
    grid_numbers: list[int],
    grid_stars: list[int] | None,
    draw_numbers: list[int],
    draw_stars: list[int] | None,
) -> tuple[list[int], list[int] | None, int, int]:
    """Compare a grid against a draw. Returns (matched_numbers, matched_stars, match_count, star_match_count)."""
    matched_numbers = sorted(set(grid_numbers) & set(draw_numbers))
    match_count = len(matched_numbers)

    matched_stars = None
    star_match_count = 0
    if grid_stars and draw_stars:
        matched_stars = sorted(set(grid_stars) & set(draw_stars))
        star_match_count = len(matched_stars)

    return matched_numbers, matched_stars, match_count, star_match_count


def determine_prize_rank(
    match_count: int,
    star_match_count: int,
    prize_tiers: list[dict[str, Any]],
) -> tuple[int | None, float]:
    """Determine the prize rank and estimated prize for given match counts.

    prize_tiers: list of dicts with keys: rank, match_numbers, match_stars, avg_prize

    Returns (rank, estimated_prize) or (None, 0.0) if no match.
    """
    for tier in sorted(prize_tiers, key=lambda t: t["rank"]):
        if match_count >= tier["match_numbers"] and star_match_count >= tier["match_stars"]:
            # Find best matching rank (most specific)
            pass

    # Find the exact match — iterate from best rank to worst
    best_rank = None
    best_prize = 0.0

    for tier in sorted(prize_tiers, key=lambda t: t["rank"]):
        if match_count == tier["match_numbers"] and star_match_count == tier["match_stars"]:
            best_rank = tier["rank"]
            best_prize = tier["avg_prize"]
            break

    return best_rank, best_prize


class AutomationService:
    """Check played grids against draws and compute results."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._result_repo = GridDrawResultRepository(session)

    async def check_played_grids(self, game_id: int) -> list[GridDrawResult]:
        """Check all played grids for a game against the latest draw."""
        # Get latest draw
        stmt = select(Draw).where(Draw.game_id == game_id).order_by(Draw.draw_date.desc()).limit(1)
        result = await self._session.execute(stmt)
        latest_draw = result.scalar_one_or_none()
        if latest_draw is None:
            return []

        # Get all played grids for this game
        stmt = select(ScoredGrid).where(
            ScoredGrid.game_id == game_id,
            ScoredGrid.is_played == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        played_grids = list(result.scalars().all())

        if not played_grids:
            return []

        # Get prize tiers
        stmt = select(GamePrizeTier).where(GamePrizeTier.game_id == game_id)
        result = await self._session.execute(stmt)
        prize_tiers = [
            {
                "rank": pt.rank,
                "match_numbers": pt.match_numbers,
                "match_stars": pt.match_stars,
                "avg_prize": pt.avg_prize,
            }
            for pt in result.scalars().all()
        ]

        results: list[GridDrawResult] = []

        for grid in played_grids:
            # Check if already processed
            already_checked = await self._result_repo.exists(grid.id, latest_draw.id)
            if already_checked:
                continue

            matched_numbers, matched_stars, match_count, star_match_count = compare_grid_to_draw(
                grid.numbers,
                grid.stars,
                latest_draw.numbers,
                latest_draw.stars,
            )

            prize_rank, estimated_prize = determine_prize_rank(
                match_count, star_match_count, prize_tiers
            )

            grid_result = GridDrawResult(
                scored_grid_id=grid.id,
                draw_id=latest_draw.id,
                matched_numbers=matched_numbers,
                matched_stars=matched_stars,
                match_count=match_count,
                star_match_count=star_match_count,
                prize_rank=prize_rank,
                estimated_prize=estimated_prize,
                checked_at=datetime.now(UTC),
            )
            grid_result = await self._result_repo.create(grid_result)
            results.append(grid_result)

            logger.info(
                "grid_checked",
                grid_id=grid.id,
                draw_id=latest_draw.id,
                match_count=match_count,
                star_match_count=star_match_count,
                prize_rank=prize_rank,
            )

        return results

    async def get_grid_results(
        self, game_id: int, user_id: int, *, limit: int = 50
    ) -> list[GridDrawResult]:
        """Get recent grid draw results for a user."""
        # Get user's played grid IDs for this game
        stmt = select(ScoredGrid.id).where(
            ScoredGrid.game_id == game_id,
            ScoredGrid.user_id == user_id,
            ScoredGrid.is_played == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        grid_ids = list(result.scalars().all())
        return await self._result_repo.get_recent_results(grid_ids, limit=limit)
