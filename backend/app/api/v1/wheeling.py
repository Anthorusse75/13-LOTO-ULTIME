"""Wheeling API — preview, generate, history, and management of wheeling systems."""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from app.core.rate_limit import limiter

from app.core.game_definitions import GameConfig
from app.dependencies import get_game_config, get_wheeling_service, require_role
from app.models.user import User, UserRole
from app.dependencies import get_current_user
from app.schemas.wheeling import (
    GainScenarioSchema,
    WheelingGenerateRequest,
    WheelingGenerateResponse,
    WheelingGridItem,
    WheelingPreviewRequest,
    WheelingPreviewResponse,
    WheelingSystemResponse,
)
from app.services.wheeling import WheelingService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.post("/preview", response_model=WheelingPreviewResponse)
@limiter.limit("30/minute")
async def preview_wheeling(
    request: Request,
    body: WheelingPreviewRequest,
    game_config: GameConfig = Depends(get_game_config),
    service: WheelingService = Depends(get_wheeling_service),
) -> WheelingPreviewResponse:
    """Quick estimation of wheeling system metrics (no generation)."""
    _validate_inputs(body.numbers, body.stars, body.guarantee, game_config)
    return await service.preview(game_config, body.numbers, body.stars, body.guarantee)


@router.post("/generate", response_model=WheelingGenerateResponse)
@limiter.limit("10/minute")
async def generate_wheeling(
    request: Request,
    body: WheelingGenerateRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: WheelingService = Depends(get_wheeling_service),
    user: User = Depends(get_current_user),
) -> WheelingGenerateResponse:
    """Generate a full wheeling system and persist it."""
    _validate_inputs(body.numbers, body.stars, body.guarantee, game_config)

    result, system = await service.generate(
        game_id=game_id,
        game_config=game_config,
        user_id=user.id,
        numbers=body.numbers,
        stars=body.stars,
        guarantee=body.guarantee,
    )

    return WheelingGenerateResponse(
        id=system.id,
        grids=[WheelingGridItem(numbers=g.numbers, stars=g.stars) for g in result.grids],
        grid_count=result.grid_count,
        total_cost=result.total_cost,
        coverage_rate=result.coverage_rate,
        reduction_rate=result.reduction_rate,
        total_t_combinations=result.total_t_combinations,
        full_wheel_size=result.full_wheel_size,
        computation_time_ms=result.computation_time_ms,
        gain_scenarios=[
            GainScenarioSchema(
                rank=s.rank,
                name=s.name,
                match_numbers=s.match_numbers,
                match_stars=s.match_stars,
                avg_prize=s.avg_prize,
                matching_grids_best=s.matching_grids_best,
                matching_grids_avg=s.matching_grids_avg,
                matching_grids_worst=s.matching_grids_worst,
                potential_gain_best=s.potential_gain_best,
                potential_gain_avg=s.potential_gain_avg,
                potential_gain_worst=s.potential_gain_worst,
            )
            for s in result.gain_scenarios
        ],
        number_distribution=result.number_distribution,
    )


@router.get("/history", response_model=list[WheelingSystemResponse])
async def get_wheeling_history(
    game_id: int = Path(..., gt=0),
    service: WheelingService = Depends(get_wheeling_service),
    user: User = Depends(get_current_user),
) -> list[WheelingSystemResponse]:
    """List saved wheeling systems for the current user and game."""
    systems = await service.get_user_systems(user.id, game_id)
    return [WheelingSystemResponse.model_validate(s) for s in systems]


@router.get("/{system_id}", response_model=WheelingSystemResponse)
async def get_wheeling_system(
    system_id: int = Path(..., gt=0),
    service: WheelingService = Depends(get_wheeling_service),
    user: User = Depends(get_current_user),
) -> WheelingSystemResponse:
    """Get a specific wheeling system by ID."""
    system = await service.get_system(system_id)
    if system is None or system.user_id != user.id:
        raise HTTPException(status_code=404, detail="Wheeling system not found")
    return WheelingSystemResponse.model_validate(system)


@router.delete("/{system_id}", status_code=204)
async def delete_wheeling_system(
    system_id: int = Path(..., gt=0),
    service: WheelingService = Depends(get_wheeling_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a wheeling system."""
    deleted = await service.delete_system(system_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wheeling system not found")


def _validate_inputs(
    numbers: list[int],
    stars: list[int] | None,
    guarantee: int,
    game_config: GameConfig,
) -> None:
    """Validate wheeling inputs against game config."""
    k = game_config.numbers_drawn
    n = len(numbers)

    if n > 20:
        raise HTTPException(status_code=422, detail="Maximum 20 numbers allowed")
    if n < k + 1:
        raise HTTPException(
            status_code=422,
            detail=f"Need at least {k + 1} numbers (k+1) for a reduced system",
        )
    if guarantee < 2 or guarantee > k:
        raise HTTPException(
            status_code=422,
            detail=f"Guarantee must be between 2 and {k}",
        )

    # Validate number range
    for num in numbers:
        if num < game_config.min_number or num > game_config.max_number:
            raise HTTPException(
                status_code=422,
                detail=f"Number {num} out of range [{game_config.min_number}-{game_config.max_number}]",
            )
    if len(set(numbers)) != len(numbers):
        raise HTTPException(status_code=422, detail="Duplicate numbers not allowed")

    # Validate stars
    if stars:
        if not game_config.stars_pool:
            raise HTTPException(status_code=422, detail="This game has no stars/chance")
        for s in stars:
            if s < 1 or s > game_config.stars_pool:
                raise HTTPException(
                    status_code=422,
                    detail=f"Star {s} out of range [1-{game_config.stars_pool}]",
                )
        if len(set(stars)) != len(stars):
            raise HTTPException(status_code=422, detail="Duplicate stars not allowed")
