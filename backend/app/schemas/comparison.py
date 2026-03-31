"""Comparison schemas — strategy comparison request/response."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StrategyConfig(BaseModel):
    type: str = Field(
        ...,
        pattern=r"^(top|portfolio|random|wheeling|budget|profile|method)$",
    )
    count: int = Field(10, gt=0, le=100)
    # Optional params depending on type
    numbers: list[int] | None = None
    stars: list[int] | None = None
    guarantee: int | None = None
    profile: str | None = None
    method: str | None = None
    budget: float | None = None
    objective: str | None = None


class ComparisonRequest(BaseModel):
    strategies: list[StrategyConfig] = Field(..., min_length=2, max_length=5)
    include_gain_scenarios: bool = False


class StrategyMetrics(BaseModel):
    type: str
    label: str
    grid_count: int
    grids: list[dict] | None = None
    avg_score: float | None = None
    score_variance: float | None = None
    diversity: float | None = None
    coverage: float | None = None
    cost: float = 0.0
    robustness: float | None = None
    expected_gain: float | None = None


class ComparisonSummary(BaseModel):
    best_score: str | None = None
    best_diversity: str | None = None
    best_coverage: str | None = None
    best_cost: str | None = None
    recommendation: str


class ComparisonResponse(BaseModel):
    strategies: list[StrategyMetrics]
    summary: ComparisonSummary
