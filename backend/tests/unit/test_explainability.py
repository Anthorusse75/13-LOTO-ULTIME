"""Unit tests for explainability engine (TEST-10)."""

import pytest

from app.engines.explainability import Explanation
from app.engines.explainability.grid_explainer import explain_grid
from app.engines.explainability.portfolio_explainer import explain_portfolio
from app.engines.explainability.simulation_explainer import explain_simulation
from app.engines.explainability.wheeling_explainer import explain_wheeling
from app.engines.explainability.comparison_explainer import explain_comparison


SAMPLE_BREAKDOWN = {
    "frequency": 0.8,
    "gap": 0.7,
    "cooccurrence": 0.6,
    "structure": 0.75,
    "balance": 0.9,
    "pattern_penalty": 0.05,
}


class TestExplanationDataclass:
    def test_explanation_defaults(self):
        e = Explanation(summary="S", interpretation="I", technical="T")
        assert e.highlights == []
        assert e.warnings == []

    def test_explanation_with_lists(self):
        e = Explanation(
            summary="S", interpretation="I", technical="T",
            highlights=["h1"], warnings=["w1"],
        )
        assert e.highlights == ["h1"]
        assert e.warnings == ["w1"]


class TestGridExplainer:
    def test_excellent_score(self):
        result = explain_grid(8.5, SAMPLE_BREAKDOWN)
        assert isinstance(result, Explanation)
        assert "8.5" in result.summary
        assert len(result.summary) > 0
        assert len(result.interpretation) > 0
        assert len(result.technical) > 0

    def test_good_score(self):
        result = explain_grid(6.0, SAMPLE_BREAKDOWN)
        assert "6.0" in result.summary

    def test_average_score(self):
        result = explain_grid(4.0, SAMPLE_BREAKDOWN)
        assert "4.0" in result.summary

    def test_weak_score(self):
        result = explain_grid(2.0, SAMPLE_BREAKDOWN)
        assert "2.0" in result.summary
        assert any("score" in w.lower() or "faible" in w.lower() for w in result.warnings)

    def test_highlights_populated(self):
        result = explain_grid(8.0, SAMPLE_BREAKDOWN)
        assert len(result.highlights) > 0

    def test_always_has_reminder_warning(self):
        result = explain_grid(9.0, SAMPLE_BREAKDOWN)
        assert any("hasard" in w or "garanti" in w or "garantit" in w or "jeu" in w.lower() for w in result.warnings)

    def test_high_penalty_warning(self):
        bd = {**SAMPLE_BREAKDOWN, "pattern_penalty": 0.8}
        result = explain_grid(5.0, bd)
        assert any("pénalité" in w.lower() or "pattern" in w.lower() for w in result.warnings)


class TestPortfolioExplainer:
    def test_high_diversity(self):
        result = explain_portfolio(
            strategy="balanced", grid_count=10,
            diversity_score=0.85, coverage_score=0.9,
            avg_grid_score=7.2,
        )
        assert isinstance(result, Explanation)
        assert "10" in result.summary
        assert len(result.highlights) > 0

    def test_medium_diversity(self):
        result = explain_portfolio(
            strategy="balanced", grid_count=5,
            diversity_score=0.5, coverage_score=0.5,
            avg_grid_score=5.0,
        )
        assert isinstance(result, Explanation)

    def test_low_diversity_warning(self):
        result = explain_portfolio(
            strategy="balanced", grid_count=3,
            diversity_score=0.2, coverage_score=0.3,
            avg_grid_score=4.0,
        )
        assert any("divers" in w.lower() for w in result.warnings)


class TestSimulationExplainer:
    def test_basic_simulation(self):
        result = explain_simulation(
            n_simulations=10000,
            avg_matches=1.5,
            expected_matches=1.4,
            match_distribution={0: 3000, 1: 4000, 2: 2000, 3: 800, 4: 150, 5: 50},
        )
        assert isinstance(result, Explanation)
        assert "1.5" in result.summary
        assert len(result.technical) > 0

    def test_low_simulation_count_warning(self):
        result = explain_simulation(
            n_simulations=100,
            avg_matches=1.5,
            expected_matches=1.4,
            match_distribution={0: 50, 1: 30, 2: 15, 3: 5},
        )
        assert any("100" in w for w in result.warnings)

    def test_high_simulation_count_highlight(self):
        result = explain_simulation(
            n_simulations=500_000,
            avg_matches=1.5,
            expected_matches=1.4,
            match_distribution={0: 150000, 1: 200000, 2: 100000, 3: 40000, 4: 8000, 5: 2000},
        )
        assert any("fiable" in h.lower() or "grand" in h.lower() for h in result.highlights)


class TestWheelingExplainer:
    def test_basic_wheeling(self):
        result = explain_wheeling(
            n_numbers=12, base=5, guarantee=3,
            n_combos=132, coverage=0.95, cost=264.0,
        )
        assert isinstance(result, Explanation)
        assert "12" in result.summary
        assert len(result.interpretation) > 0
        assert len(result.technical) > 0


class TestComparisonExplainer:
    def test_high_percentile(self):
        result = explain_comparison(
            score=8.0, rank=5, n_random=1000,
            percentile=0.95, mean_random=5.5, std_random=1.2,
        )
        assert isinstance(result, Explanation)
        assert "supérieur" in result.interpretation
        assert len(result.highlights) > 0

    def test_medium_percentile(self):
        result = explain_comparison(
            score=6.0, rank=400, n_random=1000,
            percentile=0.60, mean_random=5.5, std_random=1.2,
        )
        assert "supérieur" in result.interpretation

    def test_low_percentile(self):
        result = explain_comparison(
            score=3.0, rank=800, n_random=1000,
            percentile=0.20, mean_random=5.5, std_random=1.2,
        )
        assert "inférieur" in result.interpretation
