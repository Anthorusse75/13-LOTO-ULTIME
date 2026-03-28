"""Unit tests for simulation engines — Monte Carlo and Robustness."""

import numpy as np
import pytest
from scipy.stats import hypergeom

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer
from app.engines.simulation.monte_carlo import (
    MonteCarloSimulator,
    PortfolioSimulationResult,
    SimulationResult,
)
from app.engines.simulation.robustness import (
    ComparisonResult,
    RobustnessAnalyzer,
    StabilityResult,
)

# ── Fixtures ──

SMALL_CONFIG = GameConfig(
    name="Test",
    slug="test",
    numbers_pool=10,
    numbers_drawn=3,
    min_number=1,
    max_number=10,
)

LOTO_CONFIG = GameConfig(
    name="Loto FDJ",
    slug="loto-fdj",
    numbers_pool=49,
    numbers_drawn=5,
    min_number=1,
    max_number=49,
    stars_pool=10,
    stars_drawn=1,
    star_name="numéro chance",
)


@pytest.fixture
def small_draws():
    """50 random draws for the small game (3 numbers among 1-10)."""
    rng = np.random.default_rng(42)
    draws = []
    for _ in range(50):
        draw = sorted(rng.choice(np.arange(1, 11), size=3, replace=False).tolist())
        draws.append(draw)
    return np.array(draws)


@pytest.fixture
def small_statistics(small_draws):
    """Statistics dict for the small game."""
    from app.engines.statistics import CooccurrenceEngine, FrequencyEngine, GapEngine

    game = SMALL_CONFIG
    return {
        "frequency": FrequencyEngine().compute(small_draws, game),
        "gaps": GapEngine().compute(small_draws, game),
        "cooccurrence": CooccurrenceEngine().compute(small_draws, game),
    }


# ══════════════════════════════════════════════════════════════
# MonteCarloSimulator
# ══════════════════════════════════════════════════════════════


class TestMonteCarloSimulator:
    """Tests for MonteCarloSimulator."""

    def test_simulate_grid_returns_result(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_grid([1, 2, 3], n_simulations=1000)

        assert isinstance(result, SimulationResult)
        assert result.grid == [1, 2, 3]
        assert result.stars is None
        assert result.n_simulations == 1000
        assert sum(result.match_distribution.values()) == 1000
        assert result.star_match_distribution is None

    def test_match_distribution_keys(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_grid([1, 2, 3], n_simulations=500)

        # Keys should cover 0..k
        assert set(result.match_distribution.keys()) == {0, 1, 2, 3}

    def test_avg_matches_reasonable(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_grid([1, 2, 3], n_simulations=10000)

        # Expected: k*k/n = 3*3/10 = 0.9
        assert 0.5 < result.avg_matches < 1.5

    def test_expected_matches_formula(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_grid([1, 2, 3], n_simulations=100)

        expected = 3 * 3 / 10  # 0.9
        assert result.expected_matches == pytest.approx(expected, abs=0.001)

    def test_seed_reproducibility(self):
        r1 = MonteCarloSimulator(SMALL_CONFIG, seed=99).simulate_grid([1, 2, 3], n_simulations=500)
        r2 = MonteCarloSimulator(SMALL_CONFIG, seed=99).simulate_grid([1, 2, 3], n_simulations=500)

        assert r1.match_distribution == r2.match_distribution
        assert r1.avg_matches == r2.avg_matches

    def test_different_seeds_differ(self):
        r1 = MonteCarloSimulator(SMALL_CONFIG, seed=1).simulate_grid([1, 2, 3], n_simulations=500)
        r2 = MonteCarloSimulator(SMALL_CONFIG, seed=2).simulate_grid([1, 2, 3], n_simulations=500)

        assert r1.match_distribution != r2.match_distribution

    def test_convergence_to_hypergeometric(self):
        """With enough simulations, distribution should match theoretical."""
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_grid([1, 2, 3], n_simulations=50000)

        # Theoretical: hypergeometric(N=10, K=3, n=3)
        theoretical = MonteCarloSimulator.theoretical_distribution(10, 3)

        for m in range(4):
            empirical = result.match_distribution[m] / 50000
            assert empirical == pytest.approx(theoretical[m], abs=0.02), (
                f"m={m}: empirical={empirical:.4f}, theoretical={theoretical[m]:.4f}"
            )

    def test_simulate_grid_with_stars(self):
        sim = MonteCarloSimulator(LOTO_CONFIG, seed=42)
        result = sim.simulate_grid([1, 5, 10, 25, 49], stars=[7], n_simulations=1000)

        assert result.stars == [7]
        assert result.star_match_distribution is not None
        assert set(result.star_match_distribution.keys()) == {0, 1}
        assert sum(result.star_match_distribution.values()) == 1000

    def test_simulate_grid_no_stars_when_game_has_stars(self):
        """If stars=None but game has stars, no star distribution."""
        sim = MonteCarloSimulator(LOTO_CONFIG, seed=42)
        result = sim.simulate_grid([1, 5, 10, 25, 49], stars=None, n_simulations=100)

        assert result.star_match_distribution is None


class TestMonteCarloPortfolio:
    """Tests for portfolio simulation."""

    def test_simulate_portfolio_returns_result(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        portfolio = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = sim.simulate_portfolio(portfolio, n_simulations=1000, min_matches=2)

        assert isinstance(result, PortfolioSimulationResult)
        assert result.n_simulations == 1000
        assert 0.0 <= result.hit_rate <= 1.0
        assert result.min_matches_threshold == 2
        assert sum(result.best_match_distribution.values()) == 1000

    def test_hit_rate_increases_with_more_grids(self):
        sim1 = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        r1 = sim1.simulate_portfolio([[1, 2, 3]], n_simulations=5000, min_matches=2)

        sim2 = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        r2 = sim2.simulate_portfolio(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]], n_simulations=5000, min_matches=2
        )

        assert r2.hit_rate >= r1.hit_rate

    def test_hit_rate_decreases_with_higher_threshold(self):
        sim1 = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        r1 = sim1.simulate_portfolio([[1, 2, 3], [4, 5, 6]], n_simulations=5000, min_matches=1)

        sim2 = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        r2 = sim2.simulate_portfolio([[1, 2, 3], [4, 5, 6]], n_simulations=5000, min_matches=3)

        assert r1.hit_rate >= r2.hit_rate

    def test_avg_best_matches(self):
        sim = MonteCarloSimulator(SMALL_CONFIG, seed=42)
        result = sim.simulate_portfolio([[1, 2, 3], [4, 5, 6]], n_simulations=5000)

        # With 2 grids of 3 numbers among 10, avg best > single grid avg
        assert result.avg_best_matches > 0

    def test_portfolio_seed_reproducibility(self):
        portfolio = [[1, 2, 3], [4, 5, 6]]
        r1 = MonteCarloSimulator(SMALL_CONFIG, seed=77).simulate_portfolio(portfolio, 500)
        r2 = MonteCarloSimulator(SMALL_CONFIG, seed=77).simulate_portfolio(portfolio, 500)

        assert r1.hit_rate == r2.hit_rate
        assert r1.best_match_distribution == r2.best_match_distribution


class TestTheoreticalDistribution:
    """Tests for theoretical_distribution static method."""

    def test_loto_fdj_probabilities(self):
        dist = MonteCarloSimulator.theoretical_distribution(49, 5)

        assert len(dist) == 6  # 0..5
        assert sum(dist.values()) == pytest.approx(1.0, abs=1e-8)
        # P(0) from hypergeom(49, 5, 5)
        rv = hypergeom(49, 5, 5)
        assert dist[0] == pytest.approx(float(rv.pmf(0)), abs=1e-8)

    def test_small_game_probabilities(self):
        dist = MonteCarloSimulator.theoretical_distribution(10, 3)

        assert len(dist) == 4  # 0..3
        assert sum(dist.values()) == pytest.approx(1.0, abs=1e-8)

        # Verify against scipy directly
        rv = hypergeom(10, 3, 3)
        for m in range(4):
            assert dist[m] == pytest.approx(float(rv.pmf(m)), abs=1e-8)


# ══════════════════════════════════════════════════════════════
# RobustnessAnalyzer
# ══════════════════════════════════════════════════════════════


class TestRobustnessStability:
    """Tests for bootstrap stability analysis."""

    def test_stability_returns_result(self, small_draws):
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.analyze_stability(
            [1, 2, 3], small_draws, SMALL_CONFIG, scorer, n_bootstrap=20
        )

        assert isinstance(result, StabilityResult)
        assert 0.0 <= result.mean_score <= 1.0
        assert result.std_score >= 0.0
        assert result.cv >= 0.0
        assert 0.0 <= result.stability <= 1.0
        assert result.min_score <= result.mean_score <= result.max_score

    def test_ci95_contains_mean(self, small_draws):
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.analyze_stability(
            [1, 2, 3], small_draws, SMALL_CONFIG, scorer, n_bootstrap=50
        )

        assert result.ci_95[0] <= result.mean_score <= result.ci_95[1]

    def test_stability_seed_reproducibility(self, small_draws):
        scorer = GridScorer.from_profile("equilibre")
        r1 = RobustnessAnalyzer(seed=42).analyze_stability(
            [1, 2, 3], small_draws, SMALL_CONFIG, scorer, 30
        )
        r2 = RobustnessAnalyzer(seed=42).analyze_stability(
            [1, 2, 3], small_draws, SMALL_CONFIG, scorer, 30
        )

        assert r1.mean_score == r2.mean_score
        assert r1.stability == r2.stability

    def test_stability_is_high_for_consistent_grid(self, small_draws):
        """A grid's score should be fairly stable across bootstrap samples."""
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.analyze_stability(
            [1, 5, 10], small_draws, SMALL_CONFIG, scorer, n_bootstrap=50
        )

        # CV should be relatively small (score is stable)
        assert result.cv < 1.0
        assert result.stability > 0.0


class TestRobustnessComparison:
    """Tests for random comparison analysis."""

    def test_comparison_returns_result(self, small_statistics):
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.compare_with_random(
            grid_score=0.7,
            game=SMALL_CONFIG,
            statistics=small_statistics,
            scorer=scorer,
            n_random=200,
        )

        assert isinstance(result, ComparisonResult)
        assert result.grid_score == pytest.approx(0.7)
        assert 0.0 <= result.random_mean <= 1.0
        assert result.random_std >= 0.0
        assert 0.0 <= result.percentile <= 100.0

    def test_high_score_gives_high_percentile(self, small_statistics):
        """A very high grid score should be in a high percentile."""
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.compare_with_random(
            grid_score=0.95,
            game=SMALL_CONFIG,
            statistics=small_statistics,
            scorer=scorer,
            n_random=500,
        )

        assert result.percentile > 50.0
        assert result.z_score > 0.0

    def test_low_score_gives_low_percentile(self, small_statistics):
        """A very low grid score should be in a low percentile."""
        analyzer = RobustnessAnalyzer(seed=42)
        scorer = GridScorer.from_profile("equilibre")
        result = analyzer.compare_with_random(
            grid_score=0.05,
            game=SMALL_CONFIG,
            statistics=small_statistics,
            scorer=scorer,
            n_random=500,
        )

        assert result.percentile < 50.0
        assert result.z_score < 0.0

    def test_comparison_seed_reproducibility(self, small_statistics):
        scorer = GridScorer.from_profile("equilibre")
        r1 = RobustnessAnalyzer(seed=42).compare_with_random(
            0.5, SMALL_CONFIG, small_statistics, scorer, 200
        )
        r2 = RobustnessAnalyzer(seed=42).compare_with_random(
            0.5, SMALL_CONFIG, small_statistics, scorer, 200
        )

        assert r1.percentile == r2.percentile
        assert r1.z_score == r2.z_score
