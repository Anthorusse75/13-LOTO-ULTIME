"""Statistics endpoints — /api/v1/games/{game_id}/statistics."""

from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.exceptions import GameNotFoundError, InsufficientDataError
from app.core.game_definitions import load_all_game_configs
from app.dependencies import (
    get_game_repository,
    get_statistics_service,
    require_role,
)
from app.models.user import User, UserRole
from app.repositories.game_repository import GameRepository
from app.schemas.statistics import (
    BayesianItem,
    CentralityItem,
    CooccurrencePairItem,
    CooccurrenceResponse,
    DistributionResponse,
    EvenOddDistribution,
    FrequencyItem,
    GapItem,
    GraphResponse,
    StatisticsResponse,
    SumStats,
    TemporalResponse,
)
from app.dependencies import get_draw_repository, get_game_config
from app.repositories.draw_repository import DrawRepository
from app.services.statistics import StatisticsService

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


async def _get_snapshot(game_id: int, stats_service: StatisticsService):
    """Fetch the latest snapshot or raise 404."""
    snapshot = await stats_service.get_latest(game_id)
    if snapshot is None:
        raise InsufficientDataError(
            f"No statistics available for game_id={game_id}. Run /recompute first."
        )
    return snapshot


# ── GET /statistics — Full summary ──


@router.get("/", response_model=StatisticsResponse)
async def get_statistics(
    game_id: int,
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Get the full latest statistics summary."""
    snapshot = await _get_snapshot(game_id, stats_service)

    # Build frequency list
    frequencies = [
        FrequencyItem(number=int(num), **data) for num, data in snapshot.frequencies.items()
    ]
    frequencies.sort(key=lambda f: -f.count)

    # Build gap list
    gaps = [GapItem(number=int(num), **data) for num, data in snapshot.gaps.items()]

    # Hot / cold from frequencies
    hot_numbers = [f.number for f in frequencies[:5]]
    cold_numbers = [f.number for f in sorted(frequencies, key=lambda f: f.count)[:5]]

    # Build star statistics if available
    star_freq_items = None
    star_gap_items = None
    if snapshot.star_frequencies:
        star_freq_items = [
            FrequencyItem(number=int(num), **data)
            for num, data in snapshot.star_frequencies.items()
        ]
        star_freq_items.sort(key=lambda f: -f.count)
    if snapshot.star_gaps:
        star_gap_items = [
            GapItem(number=int(num), **data)
            for num, data in snapshot.star_gaps.items()
        ]
        star_gap_items.sort(key=lambda g: -g.current_gap)

    return StatisticsResponse(
        game_id=snapshot.game_id,
        computed_at=snapshot.computed_at,
        draw_count=snapshot.draw_count,
        frequencies=frequencies[:10],
        gaps=sorted(gaps, key=lambda g: -g.current_gap)[:10],
        hot_numbers=hot_numbers,
        cold_numbers=cold_numbers,
        distribution_entropy=snapshot.distribution_stats.get("entropy", 0),
        uniformity_score=snapshot.distribution_stats.get("uniformity_score", 0),
        star_frequencies=star_freq_items,
        star_gaps=star_gap_items,
    )


# ── GET /statistics/frequencies ──


@router.get("/frequencies", response_model=list[FrequencyItem])
async def get_frequencies(
    game_id: int,
    last_n: int | None = Query(None, ge=10, le=2000, description="Limit to the last N draws"),
    stats_service: StatisticsService = Depends(get_statistics_service),
    draw_repo: DrawRepository = Depends(get_draw_repository),
    game_config=Depends(get_game_config),
):
    """Get detailed frequency data for all numbers.

    Use `last_n` to restrict the analysis to the most recent N draws.
    """
    if last_n is not None:
        draws = await draw_repo.get_numbers_matrix(game_id, last_n=last_n)
        raw = stats_service.compute_single("frequency", draws, game_config)
        items = [FrequencyItem(number=int(num), **data) for num, data in raw.items()]
    else:
        snapshot = await _get_snapshot(game_id, stats_service)
        items = [FrequencyItem(number=int(num), **data) for num, data in snapshot.frequencies.items()]
    items.sort(key=lambda f: -f.count)
    return items


# ── GET /statistics/gaps ──


@router.get("/gaps", response_model=list[GapItem])
async def get_gaps(
    game_id: int,
    last_n: int | None = Query(None, ge=10, le=2000, description="Limit to the last N draws"),
    stats_service: StatisticsService = Depends(get_statistics_service),
    draw_repo: DrawRepository = Depends(get_draw_repository),
    game_config=Depends(get_game_config),
):
    """Get detailed gap data for all numbers.

    Use `last_n` to restrict the analysis to the most recent N draws.
    """
    if last_n is not None:
        draws = await draw_repo.get_numbers_matrix(game_id, last_n=last_n)
        raw = stats_service.compute_single("gaps", draws, game_config)
        items = [GapItem(number=int(num), **data) for num, data in raw.items()]
    else:
        snapshot = await _get_snapshot(game_id, stats_service)
        items = [GapItem(number=int(num), **data) for num, data in snapshot.gaps.items()]
    items.sort(key=lambda g: -g.current_gap)
    return items


# ── GET /statistics/cooccurrences ──


@router.get("/cooccurrences", response_model=CooccurrenceResponse)
async def get_cooccurrences(
    game_id: int,
    top_n: int = Query(50, ge=1, le=500),
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Get cooccurrence pair data."""
    snapshot = await _get_snapshot(game_id, stats_service)
    cooc = snapshot.cooccurrence_matrix

    pairs_raw = cooc.get("pairs", {})
    pairs = [CooccurrencePairItem(pair=key, **val) for key, val in pairs_raw.items()]
    pairs.sort(key=lambda p: -p.affinity)

    return CooccurrenceResponse(
        pairs=pairs[:top_n],
        expected_pair_count=cooc.get("expected_pair_count", 0),
        matrix_shape=cooc.get("matrix_shape", [0, 0]),
    )


# ── GET /statistics/temporal ──


@router.get("/temporal", response_model=TemporalResponse)
async def get_temporal(
    game_id: int,
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Get temporal trend data."""
    snapshot = await _get_snapshot(game_id, stats_service)
    return TemporalResponse(**snapshot.temporal_trends)


# ── GET /statistics/distribution ──


@router.get("/distribution", response_model=DistributionResponse)
async def get_distribution(
    game_id: int,
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Get distribution statistics."""
    snapshot = await _get_snapshot(game_id, stats_service)
    d = snapshot.distribution_stats
    return DistributionResponse(
        entropy=d["entropy"],
        max_entropy=d["max_entropy"],
        uniformity_score=d["uniformity_score"],
        chi2_statistic=d["chi2_statistic"],
        chi2_pvalue=d["chi2_pvalue"],
        is_uniform=d["is_uniform"],
        sum_stats=SumStats(**d["sum_stats"]),
        even_odd_distribution=EvenOddDistribution(**d["even_odd_distribution"]),
        decades=d.get("decades", {}),
    )


# ── GET /statistics/bayesian ──


@router.get("/bayesian", response_model=list[BayesianItem])
async def get_bayesian(
    game_id: int,
    stats_service: StatisticsService = Depends(get_statistics_service),
    _user: User = Depends(require_role(UserRole.UTILISATEUR)),
):
    """Get Bayesian posterior estimates."""
    snapshot = await _get_snapshot(game_id, stats_service)
    items = [
        BayesianItem(number=int(num), **data) for num, data in snapshot.bayesian_priors.items()
    ]
    items.sort(key=lambda b: -b.posterior_mean)
    return items


# ── GET /statistics/graph ──


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    game_id: int,
    stats_service: StatisticsService = Depends(get_statistics_service),
    _user: User = Depends(require_role(UserRole.UTILISATEUR)),
):
    """Get graph analysis metrics."""
    snapshot = await _get_snapshot(game_id, stats_service)
    g = snapshot.graph_metrics

    centrality = [
        CentralityItem(number=int(num), **data) for num, data in g.get("centrality", {}).items()
    ]
    centrality.sort(key=lambda c: -c.degree)

    return GraphResponse(
        communities=g.get("communities", []),
        centrality=centrality,
        density=g.get("density", 0),
        clustering_coefficient=g.get("clustering_coefficient", 0),
    )


# ── POST /statistics/recompute ──


@router.post("/recompute", response_model=StatisticsResponse)
@limiter.limit("5/minute")
async def recompute_statistics(
    request: Request,
    game_id: int,
    game_repo: GameRepository = Depends(get_game_repository),
    stats_service: StatisticsService = Depends(get_statistics_service),
    _user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Force full recomputation of all statistics."""
    game_def = await game_repo.get(game_id)
    if game_def is None:
        raise GameNotFoundError(f"Game {game_id} not found")

    # Load game config from YAML matching the slug
    configs = load_all_game_configs()
    game_config = configs.get(game_def.slug)
    if game_config is None:
        raise GameNotFoundError(f"No YAML config for slug '{game_def.slug}'")

    snapshot = await stats_service.compute_all(game_id, game_config)

    # Build response
    frequencies = [
        FrequencyItem(number=int(num), **data) for num, data in snapshot.frequencies.items()
    ]
    frequencies.sort(key=lambda f: -f.count)

    hot_numbers = [f.number for f in frequencies[:5]]
    cold_numbers = [f.number for f in sorted(frequencies, key=lambda f: f.count)[:5]]

    gaps = [GapItem(number=int(num), **data) for num, data in snapshot.gaps.items()]

    return StatisticsResponse(
        game_id=snapshot.game_id,
        computed_at=snapshot.computed_at,
        draw_count=snapshot.draw_count,
        frequencies=frequencies[:10],
        gaps=sorted(gaps, key=lambda g: -g.current_gap)[:10],
        hot_numbers=hot_numbers,
        cold_numbers=cold_numbers,
        distribution_entropy=snapshot.distribution_stats.get("entropy", 0),
        uniformity_score=snapshot.distribution_stats.get("uniformity_score", 0),
    )
