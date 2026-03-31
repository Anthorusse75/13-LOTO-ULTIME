"""Draws endpoints — /api/v1/games/{game_id}/draws."""

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_draw_repository, get_game_repository
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.schemas.draw import DrawResponse

router = APIRouter()


@router.get("", response_model=list[DrawResponse])
async def list_draws(
    game_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    draw_repo: DrawRepository = Depends(get_draw_repository),
    game_repo: GameRepository = Depends(get_game_repository),
) -> Any:
    """List draws for a game, ordered by date descending."""
    game = await game_repo.get(game_id)
    if game is None:
        from app.core.exceptions import GameNotFoundError

        raise GameNotFoundError(f"Game {game_id} not found")

    draws = await draw_repo.get_latest(game_id, limit=limit + skip)
    return draws[skip : skip + limit]


@router.get("/latest", response_model=DrawResponse)
async def get_latest_draw(
    game_id: int,
    draw_repo: DrawRepository = Depends(get_draw_repository),
    game_repo: GameRepository = Depends(get_game_repository),
) -> Any:
    """Get the most recent draw for a game."""
    game = await game_repo.get(game_id)
    if game is None:
        from app.core.exceptions import GameNotFoundError

        raise GameNotFoundError(f"Game {game_id} not found")

    draws = await draw_repo.get_latest(game_id, limit=1)
    if not draws:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="No draws found for this game")

    return draws[0]
