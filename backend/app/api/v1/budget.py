"""Budget API — optimize, history, and management of budget plans."""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from app.core.rate_limit import limiter

from app.core.game_definitions import GameConfig
from app.dependencies import get_budget_service, get_game_config, require_role
from app.models.user import User, UserRole
from app.dependencies import get_current_user
from app.schemas.budget import (
    BudgetOptimizeRequest,
    BudgetOptimizeResponse,
    BudgetPlanResponse,
    BudgetRecommendationSchema,
    GainScenarioSummarySchema,
)
from app.services.budget import BudgetService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.post("/optimize", response_model=BudgetOptimizeResponse)
@limiter.limit("10/minute")
async def optimize_budget(
    request: Request,
    body: BudgetOptimizeRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> BudgetOptimizeResponse:
    """Generate budget-optimized grid recommendations."""
    if body.numbers:
        _validate_numbers(body.numbers, game_config)

    result, plan = await service.optimize(
        game_id=game_id,
        game_config=game_config,
        user_id=user.id,
        budget=body.budget,
        objective=body.objective,
        numbers=body.numbers,
    )

    return BudgetOptimizeResponse(
        id=plan.id,
        budget=result.budget,
        grid_price=result.grid_price,
        max_grids=result.max_grids,
        recommendations=[
            BudgetRecommendationSchema(
                strategy=r.strategy,
                grids=r.grids,
                grid_count=r.grid_count,
                total_cost=r.total_cost,
                avg_score=r.avg_score,
                diversity_score=r.diversity_score,
                coverage_rate=r.coverage_rate,
                expected_gain=GainScenarioSummarySchema(
                    optimistic=r.expected_gain.optimistic,
                    mean=r.expected_gain.mean,
                    pessimistic=r.expected_gain.pessimistic,
                ),
                explanation=r.explanation,
                is_recommended=r.is_recommended,
            )
            for r in result.recommendations
        ],
    )


@router.get("/history", response_model=list[BudgetPlanResponse])
async def get_budget_history(
    game_id: int = Path(..., gt=0),
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> list[BudgetPlanResponse]:
    """List saved budget plans for the current user and game."""
    plans = await service.get_user_plans(user.id, game_id)
    return [BudgetPlanResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=BudgetPlanResponse)
async def get_budget_plan(
    plan_id: int = Path(..., gt=0),
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> BudgetPlanResponse:
    """Get a specific budget plan by ID."""
    plan = await service.get_plan(plan_id)
    if plan is None or plan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Budget plan not found")
    return BudgetPlanResponse.model_validate(plan)


@router.delete("/{plan_id}", status_code=204)
async def delete_budget_plan(
    plan_id: int = Path(..., gt=0),
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a budget plan."""
    deleted = await service.delete_plan(plan_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget plan not found")


def _validate_numbers(numbers: list[int], game_config: GameConfig) -> None:
    """Validate selected numbers against game config."""
    for num in numbers:
        if num < game_config.min_number or num > game_config.max_number:
            raise HTTPException(
                status_code=422,
                detail=f"Number {num} out of range [{game_config.min_number}-{game_config.max_number}]",
            )
    if len(numbers) != len(set(numbers)):
        raise HTTPException(status_code=422, detail="Duplicate numbers not allowed")
