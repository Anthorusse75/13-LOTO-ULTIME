"""Unit tests for budget engine — compute_max_grids & rank_recommendations."""

import pytest

from app.engines.budget import (
    BudgetRecommendation,
    GainScenarioSummary,
    compute_max_grids,
    rank_recommendations,
)

GAIN = GainScenarioSummary(optimistic=10.0, mean=3.0, pessimistic=0.0)


class TestComputeMaxGrids:
    def test_exact_budget(self):
        assert compute_max_grids(22.0, 2.20) == 10

    def test_partial_budget(self):
        assert compute_max_grids(5.0, 2.20) == 2

    def test_zero_price(self):
        assert compute_max_grids(10.0, 0) == 0

    def test_budget_less_than_price(self):
        assert compute_max_grids(1.0, 2.50) == 0

    def test_large_budget(self):
        assert compute_max_grids(1000.0, 2.20) == 454


class TestRankRecommendations:
    def _make_rec(self, strategy, avg_score=0.7, coverage=0.5, diversity=0.4):
        return BudgetRecommendation(
            strategy=strategy,
            grids=[],
            grid_count=5,
            total_cost=11.0,
            avg_score=avg_score,
            diversity_score=diversity,
            coverage_rate=coverage,
            expected_gain=GAIN,
            explanation="test",
        )

    def test_quality_objective(self):
        recs = [
            self._make_rec("top", avg_score=0.9),
            self._make_rec("portfolio", avg_score=0.7),
        ]
        ranked = rank_recommendations(recs, "quality")
        assert ranked[0].strategy == "top"
        assert ranked[0].is_recommended is True
        assert ranked[1].is_recommended is False

    def test_coverage_objective(self):
        recs = [
            self._make_rec("top", coverage=0.3),
            self._make_rec("wheeling", coverage=0.9, avg_score=0.0),
        ]
        ranked = rank_recommendations(recs, "coverage")
        assert ranked[0].strategy == "wheeling"
        assert ranked[0].is_recommended is True

    def test_balanced_objective(self):
        recs = [
            self._make_rec("top", avg_score=0.9, coverage=0.1, diversity=0.1),
            self._make_rec("portfolio", avg_score=0.7, coverage=0.8, diversity=0.8),
        ]
        ranked = rank_recommendations(recs, "balanced")
        # portfolio should win because coverage+diversity dominate
        assert ranked[0].strategy == "portfolio"
        assert ranked[0].is_recommended is True

    def test_empty_list(self):
        assert rank_recommendations([], "balanced") == []
