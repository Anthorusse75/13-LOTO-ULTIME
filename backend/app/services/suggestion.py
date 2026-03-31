"""Suggestion service — daily grid recommendations."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from app.repositories.grid_repository import GridRepository
from app.schemas.suggestion import DailySuggestionResponse, SuggestionGrid

logger = structlog.get_logger(__name__)


class SuggestionService:
    """Generate daily grid suggestions based on top-scoring grids."""

    def __init__(self, grid_repo: GridRepository):
        self._grid_repo = grid_repo

    async def get_daily_suggestion(
        self, game_id: int, *, count: int = 3
    ) -> DailySuggestionResponse:
        """Return top-scored grids as daily suggestions."""
        top_grids = await self._grid_repo.get_top_grids(game_id, limit=count)

        grids = [
            SuggestionGrid(
                numbers=g.numbers,
                stars=g.stars,
                total_score=g.total_score,
                method=g.method or "scoring",
            )
            for g in top_grids
        ]

        today = datetime.now(UTC).strftime("%Y-%m-%d")

        return DailySuggestionResponse(
            game_id=game_id,
            date=today,
            grids=grids,
            reason=(
                f"Les {len(grids)} grilles les mieux notées du jour, "
                "basées sur l'analyse statistique complète."
            ),
        )
