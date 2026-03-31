from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies import get_game_repository
from app.repositories.game_repository import GameRepository
from app.schemas.game import GameDefinitionResponse

router = APIRouter()


@router.get("", response_model=list[GameDefinitionResponse])
async def list_games(
    game_repo: GameRepository = Depends(get_game_repository),
) -> Any:
    """Liste tous les jeux actifs."""
    games = await game_repo.get_active_games()
    return games


@router.get("/{slug}", response_model=GameDefinitionResponse)
async def get_game(
    slug: str,
    game_repo: GameRepository = Depends(get_game_repository),
) -> Any:
    """Récupère un jeu par son slug."""
    from app.core.exceptions import GameNotFoundError

    game = await game_repo.get_by_slug(slug)
    if game is None:
        raise GameNotFoundError(f"Jeu '{slug}' non trouvé")
    return game
