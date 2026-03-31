"""Portfolios API — optimized portfolio generation and management."""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.dependencies import get_game_config, get_grid_service, require_role
from app.models.user import UserRole
from app.schemas.portfolio import (
    PortfolioGenerateRequest,
    PortfolioGenerateResponse,
)
from app.services.grid import GridService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=PortfolioGenerateResponse)
@limiter.limit("10/minute")
async def generate_portfolio(
    request: Request,
    body: PortfolioGenerateRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: GridService = Depends(get_grid_service),
) -> PortfolioGenerateResponse:
    """Generate an optimized portfolio of diverse, high-scoring grids."""

    try:
        result, method_used, elapsed_ms = await service.generate_portfolio(
            game_id=game_id,
            game=game_config,
            grid_count=body.grid_count,
            strategy=body.strategy,
            profile=body.profile,
            custom_weights=body.weights,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

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


@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(
    portfolio_id: int = Path(..., gt=0),
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
) -> None:
    """Delete a portfolio by ID."""
    deleted = await service.delete_portfolio(portfolio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio not found")
