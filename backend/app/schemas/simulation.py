"""Simulation request/response schemas."""

from pydantic import BaseModel, Field

from app.schemas.grid import ExplanationSchema

# ── Requests ──


class MonteCarloGridRequest(BaseModel):
    """Request for Monte Carlo simulation of a single grid."""

    numbers: list[int] = Field(..., min_length=1)
    stars: list[int] | None = None
    n_simulations: int = Field(10_000, ge=100, le=1_000_000)
    seed: int | None = None


class MonteCarloPortfolioRequest(BaseModel):
    """Request for Monte Carlo simulation of a portfolio."""

    grids: list[list[int]] = Field(..., min_length=1, max_length=50)
    n_simulations: int = Field(10_000, ge=100, le=1_000_000)
    min_matches: int = Field(2, ge=1, le=5)
    seed: int | None = None


class StabilityRequest(BaseModel):
    """Request for bootstrap stability analysis."""

    numbers: list[int] = Field(..., min_length=1)
    n_bootstrap: int = Field(100, ge=10, le=1000)
    profile: str = "equilibre"
    seed: int | None = None


class ComparisonRequest(BaseModel):
    """Request for random comparison analysis."""

    numbers: list[int] = Field(..., min_length=1)
    n_random: int = Field(1000, ge=100, le=100_000)
    profile: str = "equilibre"
    seed: int | None = None


# ── Responses ──


class MonteCarloGridResponse(BaseModel):
    """Response for single-grid Monte Carlo simulation."""

    grid: list[int]
    stars: list[int] | None
    n_simulations: int
    match_distribution: dict[int, int]
    star_match_distribution: dict[int, int] | None
    avg_matches: float
    expected_matches: float
    computation_time_ms: float
    explanation: ExplanationSchema | None = None


class MonteCarloPortfolioResponse(BaseModel):
    """Response for portfolio Monte Carlo simulation."""

    n_simulations: int
    hit_rate: float
    min_matches_threshold: int
    best_match_distribution: dict[int, int]
    avg_best_matches: float
    computation_time_ms: float


class StabilityResponse(BaseModel):
    """Response for bootstrap stability analysis."""

    mean_score: float
    std_score: float
    cv: float
    stability: float
    ci_95_low: float
    ci_95_high: float
    min_score: float
    max_score: float
    computation_time_ms: float


class ComparisonResponse(BaseModel):
    """Response for random comparison analysis."""

    grid_score: float
    random_mean: float
    random_std: float
    percentile: float
    z_score: float
    computation_time_ms: float
    explanation: ExplanationSchema | None = None
