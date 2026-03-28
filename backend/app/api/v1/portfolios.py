"""Portfolios API — optimized portfolio generation and management."""

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import load_all_game_configs
from app.dependencies import get_grid_service, require_role
from app.models.user import UserRole
from app.schemas.portfolio import (
    PortfolioGenerateRequest,
    PortfolioGenerateResponse,
)
from app.services.grid import GridService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])

_game_configs = load_all_game_configs()


def _get_game_config(game_id: int):
    """Resolve game config by game_id."""
    configs = list(_game_configs.values())
    for cfg in configs:
        return cfg
    raise HTTPException(status_code=404, detail="Game not found")


@router.post("/generate", response_model=PortfolioGenerateResponse)
async def generate_portfolio(
    request: PortfolioGenerateRequest,
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Generate an optimized portfolio of diverse, high-scoring grids."""
    game_config = _get_game_config(game_id)

    try:
        result, method_used, elapsed_ms = await service.generate_portfolio(
            game_id=game_id,
            game=game_config,
            grid_count=request.grid_count,
            strategy=request.strategy,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PortfolioGenerateResponse(
        strategy=result.strategy,
        grid_count=len(result.grids),
        grids=[
            {"numbers": g.numbers, "stars": g.stars, "score": g.total_score} for g in result.grids
        ],
        diversity_score=result.diversity_score,
        coverage_score=result.coverage_score,
        avg_grid_score=result.avg_grid_score,
        min_hamming_distance=result.min_hamming_distance,
        computation_time_ms=round(elapsed_ms, 1),
        method_used=method_used,
    )
