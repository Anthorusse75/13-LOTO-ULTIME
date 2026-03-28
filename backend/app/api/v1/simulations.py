"""Simulation API — Monte Carlo and robustness analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.exceptions import InsufficientDataError
from app.core.game_definitions import load_all_game_configs
from app.dependencies import get_simulation_service, require_role
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

_game_configs = load_all_game_configs()


def _get_game_config(game_id: int):
    """Resolve game config by game_id."""
    configs = list(_game_configs.values())
    for cfg in configs:
        return cfg
    raise HTTPException(status_code=404, detail="Game not found")


@router.post("/monte-carlo", response_model=MonteCarloGridResponse)
async def simulate_grid(
    request: MonteCarloGridRequest,
    game_id: int = Path(..., gt=0),
    service: SimulationService = Depends(get_simulation_service),
):
    """Run Monte Carlo simulation on a single grid."""
    game_config = _get_game_config(game_id)

    result, elapsed_ms = await service.simulate_grid(
        game_id=game_id,
        game=game_config,
        grid=request.numbers,
        stars=request.stars,
        n_simulations=request.n_simulations,
        seed=request.seed,
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
async def simulate_portfolio(
    request: MonteCarloPortfolioRequest,
    game_id: int = Path(..., gt=0),
    service: SimulationService = Depends(get_simulation_service),
):
    """Run Monte Carlo simulation on a portfolio of grids."""
    game_config = _get_game_config(game_id)

    result, elapsed_ms = await service.simulate_portfolio(
        game_id=game_id,
        game=game_config,
        portfolio=request.grids,
        n_simulations=request.n_simulations,
        min_matches=request.min_matches,
        seed=request.seed,
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
async def analyze_stability(
    request: StabilityRequest,
    game_id: int = Path(..., gt=0),
    service: SimulationService = Depends(get_simulation_service),
):
    """Bootstrap stability analysis for a grid."""
    game_config = _get_game_config(game_id)

    try:
        result, elapsed_ms = await service.analyze_stability(
            game_id=game_id,
            game=game_config,
            grid=request.numbers,
            n_bootstrap=request.n_bootstrap,
            profile=request.profile,
            seed=request.seed,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

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
async def compare_with_random(
    request: ComparisonRequest,
    game_id: int = Path(..., gt=0),
    service: SimulationService = Depends(get_simulation_service),
):
    """Compare a grid's score against random grids."""
    game_config = _get_game_config(game_id)

    try:
        result, elapsed_ms = await service.compare_with_random(
            game_id=game_id,
            game=game_config,
            grid=request.numbers,
            n_random=request.n_random,
            profile=request.profile,
            seed=request.seed,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return ComparisonResponse(
        grid_score=result.grid_score,
        random_mean=result.random_mean,
        random_std=result.random_std,
        percentile=result.percentile,
        z_score=result.z_score,
        computation_time_ms=round(elapsed_ms, 1),
    )
