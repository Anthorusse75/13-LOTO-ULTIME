"""Grids API — scoring, generation, and grid management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.dependencies import get_game_config, get_grid_service, require_role
from app.models.user import UserRole
from app.schemas.grid import (
    GridGenerateRequest,
    GridGenerateResponse,
    GridResponse,
    GridScoreRequest,
    GridScoreResponse,
)
from app.services.grid import GridService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])
limiter = Limiter(key_func=get_remote_address)


@router.post("/score", response_model=GridScoreResponse)
async def score_grid(
    request: GridScoreRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: GridService = Depends(get_grid_service),
):
    """Score a grid against the latest statistics snapshot."""

    try:
        result = await service.score_grid(
            game_id=game_id,
            game=game_config,
            numbers=request.numbers,
            stars=request.stars,
            profile=request.profile,
            custom_weights=request.weights,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return GridScoreResponse(
        numbers=result.numbers,
        stars=result.stars,
        total_score=result.total_score,
        score_breakdown=result.score_breakdown,
        star_score=result.star_score,
    )


@router.post("/generate", response_model=GridGenerateResponse)
@limiter.limit("10/minute")
async def generate_grids(
    request: Request,
    body: GridGenerateRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: GridService = Depends(get_grid_service),
):
    """Generate optimized grids using meta-heuristics."""

    try:
        results, method_used, elapsed_ms = await service.generate_grids(
            game_id=game_id,
            game=game_config,
            count=body.count,
            method=body.method,
            profile=body.profile,
            custom_weights=body.weights,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return GridGenerateResponse(
        grids=[
            GridScoreResponse(
                numbers=r.numbers,
                stars=r.stars,
                total_score=r.total_score,
                score_breakdown=r.score_breakdown,
                star_score=r.star_score,
            )
            for r in results
        ],
        computation_time_ms=round(elapsed_ms, 1),
        method_used=method_used,
    )


@router.get("/top", response_model=list[GridResponse])
async def get_top_grids(
    game_id: int = Path(..., gt=0),
    limit: int = Query(10, ge=1, le=100),
    service: GridService = Depends(get_grid_service),
):
    """Return top-scored grids for a game."""
    grids = await service.get_top_grids(game_id, limit)
    return grids


@router.get("/{grid_id}", response_model=GridResponse)
async def get_grid(
    grid_id: int = Path(..., gt=0),
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Return a single grid by ID."""
    grid = await service.get_grid(grid_id)
    if grid is None:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid


@router.delete("/{grid_id}", status_code=204)
async def delete_grid(
    grid_id: int = Path(..., gt=0),
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Delete a grid by ID."""
    deleted = await service.delete_grid(grid_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grid not found")


@router.patch("/{grid_id}/favorite", response_model=GridResponse)
async def toggle_favorite(
    grid_id: int = Path(..., gt=0),
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Toggle the favorite status of a grid."""
    grid = await service.toggle_favorite(grid_id)
    if grid is None:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid


@router.patch("/{grid_id}/played", response_model=GridResponse)
async def toggle_played(
    grid_id: int = Path(..., gt=0),
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Toggle the played status of a grid."""
    grid = await service.toggle_played(grid_id)
    if grid is None:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid


@router.get("/favorites", response_model=list[GridResponse])
async def get_favorites(
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Return all favorite grids for a game."""
    return await service.get_favorites(game_id)


@router.get("/played", response_model=list[GridResponse])
async def get_played_grids(
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Return all grids marked as played for a game."""
    return await service.get_played_grids(game_id)
