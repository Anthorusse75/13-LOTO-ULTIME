"""Comparison API — compare multiple strategies."""

import structlog
from fastapi import APIRouter, Depends, Path, Request

logger = structlog.get_logger(__name__)

from app.core.game_definitions import GameConfig
from app.core.rate_limit import limiter
from app.dependencies import (
    get_comparison_service,
    get_current_user,
    get_game_config,
    require_role,
)
from app.models.user import User, UserRole
from app.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummary,
    StrategyMetrics,
)
from app.services.comparison import ComparisonService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.post("/compare", response_model=ComparisonResponse)
@limiter.limit("5/minute")
async def compare_strategies(
    request: Request,
    body: ComparisonRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: ComparisonService = Depends(get_comparison_service),
    user: User = Depends(get_current_user),
) -> ComparisonResponse:
    """Compare 2-5 strategies side by side with unified metrics."""
    logger.info(
        "comparison_request",
        game_id=game_id,
        strategy_count=len(body.strategies),
        include_gains=body.include_gain_scenarios,
        user_id=user.id,
    )
    strategies_dicts = [s.model_dump() for s in body.strategies]

    result = await service.compare(
        game_id=game_id,
        game=game_config,
        strategies=strategies_dicts,
        include_gains=body.include_gain_scenarios,
    )

    return ComparisonResponse(
        strategies=[StrategyMetrics(**s) for s in result["strategies"]],
        summary=ComparisonSummary(**result["summary"]),
    )
