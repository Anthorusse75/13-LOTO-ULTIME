"""Budget optimizer — recommends the best grid allocation for a given budget.

Generates multiple strategy recommendations (top, portfolio, wheeling)
and ranks them according to the user's objective.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GainScenarioSummary:
    """Simplified gain scenario for budget recommendations."""

    optimistic: float
    mean: float
    pessimistic: float


@dataclass(frozen=True)
class BudgetRecommendation:
    """A single strategy recommendation within a budget plan."""

    strategy: str  # 'top', 'portfolio', 'wheeling'
    grids: list[dict[str, Any]]
    grid_count: int
    total_cost: float
    avg_score: float | None
    diversity_score: float | None
    coverage_rate: float | None
    expected_gain: GainScenarioSummary
    explanation: str
    is_recommended: bool = False


@dataclass(frozen=True)
class BudgetOptimizationResult:
    """Full result of budget optimization."""

    budget: float
    grid_price: float
    max_grids: int
    recommendations: list[BudgetRecommendation]


def compute_max_grids(budget: float, grid_price: float) -> int:
    """Maximum number of grids affordable within the budget."""
    if grid_price <= 0:
        return 0
    return math.floor(budget / grid_price)


def rank_recommendations(
    recommendations: list[BudgetRecommendation],
    objective: str,
) -> list[BudgetRecommendation]:
    """Sort recommendations and mark the best one according to objective.

    Objectives:
    - 'quality': maximize avg_score
    - 'coverage': maximize coverage_rate
    - 'balanced': weighted balance of score + coverage + diversity
    """

    def _score(r: BudgetRecommendation) -> float:
        avg = r.avg_score or 0.0
        cov = r.coverage_rate or 0.0
        div = r.diversity_score or 0.0

        if objective == "quality":
            return avg
        elif objective == "coverage":
            return cov * 100 + avg * 0.1
        else:  # balanced
            return avg * 0.4 + cov * 30 + div * 30

    sorted_recs = sorted(recommendations, key=_score, reverse=True)

    if not sorted_recs:
        return sorted_recs

    # Mark top as recommended
    result: list[BudgetRecommendation] = []
    for i, rec in enumerate(sorted_recs):
        if i == 0:
            result.append(BudgetRecommendation(
                strategy=rec.strategy,
                grids=rec.grids,
                grid_count=rec.grid_count,
                total_cost=rec.total_cost,
                avg_score=rec.avg_score,
                diversity_score=rec.diversity_score,
                coverage_rate=rec.coverage_rate,
                expected_gain=rec.expected_gain,
                explanation=rec.explanation,
                is_recommended=True,
            ))
        else:
            result.append(rec)
    return result
