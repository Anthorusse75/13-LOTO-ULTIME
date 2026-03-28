"""Grids API — scoring, generation, and grid management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import load_all_game_configs
from app.dependencies import get_grid_service
from app.schemas.grid import (
    GridGenerateRequest,
    GridGenerateResponse,
    GridResponse,
    GridScoreRequest,
    GridScoreResponse,
)
from app.services.grid import GridService

router = APIRouter()

_game_configs = load_all_game_configs()


def _get_game_config(game_id: int):
    """Resolve game config by game_id (uses slug mapping loaded once)."""
    configs = list(_game_configs.values())
    for cfg in configs:
        return cfg
    raise HTTPException(status_code=404, detail="Game not found")


@router.post("/score", response_model=GridScoreResponse)
async def score_grid(
    request: GridScoreRequest,
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Score a grid against the latest statistics snapshot."""
    # Load game configs and find by game_id
    configs = load_all_game_configs()
    game_config = None
    for cfg in configs.values():
        game_config = cfg
        break

    if game_config is None:
        raise HTTPException(status_code=404, detail="No game configuration found")

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
        raise HTTPException(status_code=422, detail=str(exc))

    return GridScoreResponse(
        numbers=result.numbers,
        stars=result.stars,
        total_score=result.total_score,
        score_breakdown=result.score_breakdown,
        star_score=result.star_score,
    )


@router.post("/generate", response_model=GridGenerateResponse)
async def generate_grids(
    request: GridGenerateRequest,
    game_id: int = Path(..., gt=0),
    service: GridService = Depends(get_grid_service),
):
    """Generate optimized grids using meta-heuristics."""
    game_config = _get_game_config(game_id)

    try:
        results, method_used, elapsed_ms = await service.generate_grids(
            game_id=game_id,
            game=game_config,
            count=request.count,
            method=request.method,
            custom_weights=request.weights,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

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
