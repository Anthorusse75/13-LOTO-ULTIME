"""Simulation API — Monte Carlo and robustness analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from app.core.rate_limit import limiter

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import GameConfig
from app.dependencies import get_game_config, get_simulation_service, require_role
from app.models.user import UserRole
from app.schemas.simulation import (
    ComparisonRequest,
    ComparisonResponse,
    MonteCarloGridRequest,
    MonteCarloGridResponse,
    MonteCarloPortfolioRequest,
    MonteCarloPortfolioResponse,
    StabilityRequest,
    StabilityResponse,
)
from app.services.simulation import SimulationService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.post("/monte-carlo", response_model=MonteCarloGridResponse)
@limiter.limit("10/minute")
async def simulate_grid(
    request: Request,
    body: MonteCarloGridRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: SimulationService = Depends(get_simulation_service),
) -> MonteCarloGridResponse:
    """Run Monte Carlo simulation on a single grid."""

    result, elapsed_ms = await service.simulate_grid(
        game_id=game_id,
        game=game_config,
        grid=body.numbers,
        stars=body.stars,
        n_simulations=body.n_simulations,
        seed=body.seed,
    )

    return MonteCarloGridResponse(
        grid=result.grid,
        stars=result.stars,
        n_simulations=result.n_simulations,
        match_distribution=result.match_distribution,
        star_match_distribution=result.star_match_distribution,
        avg_matches=result.avg_matches,
        expected_matches=result.expected_matches,
        computation_time_ms=round(elapsed_ms, 1),
    )


@router.post("/monte-carlo/portfolio", response_model=MonteCarloPortfolioResponse)
@limiter.limit("10/minute")
async def simulate_portfolio(
    request: Request,
    body: MonteCarloPortfolioRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: SimulationService = Depends(get_simulation_service),
) -> MonteCarloPortfolioResponse:
    """Run Monte Carlo simulation on a portfolio of grids."""

    result, elapsed_ms = await service.simulate_portfolio(
        game_id=game_id,
        game=game_config,
        portfolio=body.grids,
        n_simulations=body.n_simulations,
        min_matches=body.min_matches,
        seed=body.seed,
    )

    return MonteCarloPortfolioResponse(
        n_simulations=result.n_simulations,
        hit_rate=result.hit_rate,
        min_matches_threshold=result.min_matches_threshold,
        best_match_distribution=result.best_match_distribution,
        avg_best_matches=result.avg_best_matches,
        computation_time_ms=round(elapsed_ms, 1),
    )


@router.post("/stability", response_model=StabilityResponse)
@limiter.limit("10/minute")
async def analyze_stability(
    request: Request,
    body: StabilityRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: SimulationService = Depends(get_simulation_service),
) -> StabilityResponse:
    """Bootstrap stability analysis for a grid."""

    try:
        result, elapsed_ms = await service.analyze_stability(
            game_id=game_id,
            game=game_config,
            grid=body.numbers,
            n_bootstrap=body.n_bootstrap,
            profile=body.profile,
            seed=body.seed,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return StabilityResponse(
        mean_score=result.mean_score,
        std_score=result.std_score,
        cv=result.cv,
        stability=result.stability,
        ci_95_low=result.ci_95[0],
        ci_95_high=result.ci_95[1],
        min_score=result.min_score,
        max_score=result.max_score,
        computation_time_ms=round(elapsed_ms, 1),
    )


@router.post("/compare-random", response_model=ComparisonResponse)
@limiter.limit("10/minute")
async def compare_with_random(
    request: Request,
    body: ComparisonRequest,
    game_id: int = Path(..., gt=0),
    game_config: GameConfig = Depends(get_game_config),
    service: SimulationService = Depends(get_simulation_service),
) -> ComparisonResponse:
    """Compare a grid's score against random grids."""

    try:
        result, elapsed_ms = await service.compare_with_random(
            game_id=game_id,
            game=game_config,
            grid=body.numbers,
            n_random=body.n_random,
            profile=body.profile,
            seed=body.seed,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ComparisonResponse(
        grid_score=result.grid_score,
        random_mean=result.random_mean,
        random_std=result.random_std,
        percentile=result.percentile,
        z_score=result.z_score,
        computation_time_ms=round(elapsed_ms, 1),
    )
