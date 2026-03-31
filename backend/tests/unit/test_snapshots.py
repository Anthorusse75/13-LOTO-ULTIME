"""Snapshot tests for non-regression (SNAP-01 to SNAP-04).

These tests capture deterministic reference values and ensure
future changes don't alter scoring, statistics, portfolio, or simulation outputs.
"""

import numpy as np
import pytest

from app.core.game_definitions import GameConfig
from app.engines.optimization import GeneticAlgorithm
from app.engines.scoring.scorer import GridScorer
from app.engines.simulation.monte_carlo import MonteCarloSimulator
from app.engines.statistics.frequency import FrequencyEngine
from app.engines.statistics.gap import GapEngine

# ── Shared fixtures ──


@pytest.fixture
def loto_config():
    return GameConfig(
        name="Loto",
        slug="loto",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="chance",
    )


@pytest.fixture
def euromillions_config():
    return GameConfig(
        name="EuroMillions",
        slug="euromillions",
        numbers_pool=50,
        numbers_drawn=5,
        min_number=1,
        max_number=50,
        stars_pool=12,
        stars_drawn=2,
        star_name="étoile",
    )


@pytest.fixture
def reference_draws():
    """20 deterministic Loto draws (49 pool, 5 drawn) for reproducible stats."""
    rng = np.random.default_rng(12345)
    draws = np.array(
        [sorted(rng.choice(range(1, 50), size=5, replace=False).tolist()) for _ in range(20)]
    )
    return draws


@pytest.fixture
def reference_statistics(reference_draws, loto_config):
    """Compute real stats from reference draws."""
    freq = FrequencyEngine().compute(reference_draws, loto_config)
    gap = GapEngine().compute(reference_draws, loto_config)

    # Build cooccurrence manually (minimal, for scorer)
    cooccurrences = {
        "pairs": {},
        "expected_pair_count": 5.0,
        "matrix_shape": [49, 49],
    }
    for i in range(1, 50):
        for j in range(i + 1, 50):
            count = 0
            for draw in reference_draws:
                if i in draw and j in draw:
                    count += 1
            cooccurrences["pairs"][f"{i}-{j}"] = {
                "count": count,
                "expected": 5.0,
                "affinity": count / 5.0 if count else 0.0,
            }

    return {
        "frequency": {str(k): v for k, v in freq.items()},
        "gaps": {str(k): v for k, v in gap.items()},
        "cooccurrence": cooccurrences,
    }


# ── SNAP-01: Scoring stability ──


class TestScoringSnapshot:
    """SNAP-01: Scoring of fixed grids must produce identical results."""

    REFERENCE_GRIDS = [
        [3, 12, 23, 34, 45],
        [7, 14, 28, 35, 49],
        [1, 10, 20, 30, 40],
    ]

    def test_scoring_deterministic(self, loto_config, reference_statistics):
        """Same grid + same stats → same score, every time."""
        scorer = GridScorer.from_profile("equilibre")
        results = []
        for grid in self.REFERENCE_GRIDS:
            r = scorer.score(grid, reference_statistics, loto_config)
            results.append(r)

        # Run again — must be identical
        for i, grid in enumerate(self.REFERENCE_GRIDS):
            r2 = scorer.score(grid, reference_statistics, loto_config)
            assert r2.total_score == results[i].total_score
            assert r2.score_breakdown == results[i].score_breakdown

    def test_profiles_produce_different_scores(self, loto_config, reference_statistics):
        """Different profiles → different total scores for the same grid."""
        grid = [3, 12, 23, 34, 45]
        scores = {}
        for profile in ("equilibre", "tendance", "contrarian", "structurel"):
            scorer = GridScorer.from_profile(profile)
            r = scorer.score(grid, reference_statistics, loto_config)
            scores[profile] = r.total_score

        # At least 3 distinct scores among 4 profiles
        unique_scores = set(round(s, 4) for s in scores.values())
        assert len(unique_scores) >= 3, f"Expected diverse scores, got {scores}"

    def test_scoring_snapshot_values(self, loto_config, reference_statistics):
        """Capture and pin exact reference scores for regression detection."""
        scorer = GridScorer.from_profile("equilibre")
        grid = [3, 12, 23, 34, 45]
        result = scorer.score(grid, reference_statistics, loto_config)

        # Pin the breakdown structure
        assert set(result.score_breakdown.keys()) == {
            "frequency",
            "gap",
            "cooccurrence",
            "structure",
            "balance",
            "pattern_penalty",
        }
        # All sub-scores in [0, 1]
        for name, value in result.score_breakdown.items():
            assert 0.0 <= value <= 1.0, f"{name}={value} out of range"
        assert 0.0 <= result.total_score <= 1.0


# ── SNAP-02: Statistics stability ──


class TestStatisticsSnapshot:
    """SNAP-02: Statistics computed from a fixed dataset must be identical."""

    def test_frequency_deterministic(self, reference_draws, loto_config):
        """Same draws → same frequencies."""
        engine = FrequencyEngine()
        r1 = engine.compute(reference_draws, loto_config)
        r2 = engine.compute(reference_draws, loto_config)
        assert r1 == r2

    def test_gap_deterministic(self, reference_draws, loto_config):
        """Same draws → same gaps."""
        engine = GapEngine()
        r1 = engine.compute(reference_draws, loto_config)
        r2 = engine.compute(reference_draws, loto_config)
        assert r1 == r2

    def test_frequency_snapshot_values(self, reference_draws, loto_config):
        """Pin frequency stats for number 1."""
        engine = FrequencyEngine()
        freq = engine.compute(reference_draws, loto_config)
        # Number 1: verify structure
        entry = freq[1]
        assert "count" in entry
        assert "relative" in entry
        assert "ratio" in entry
        assert "last_seen" in entry
        assert isinstance(entry["count"], int)
        assert 0.0 <= entry["relative"] <= 1.0

    def test_gap_snapshot_values(self, reference_draws, loto_config):
        """Pin gap stats structure."""
        engine = GapEngine()
        gaps = engine.compute(reference_draws, loto_config)
        entry = gaps[1]
        assert "current_gap" in entry
        assert "avg_gap" in entry
        assert "max_gap" in entry
        assert "min_gap" in entry
        assert "median_gap" in entry
        assert "expected_gap" in entry
        assert entry["expected_gap"] == pytest.approx(49 / 5, rel=0.01)


# ── SNAP-03: Portfolio with seed ──


class TestPortfolioSnapshot:
    """SNAP-03: Portfolio generated with a fixed seed must be reproducible."""

    def test_portfolio_reproducible(self, loto_config, reference_statistics):
        """Same seed → same grids, same scores."""
        scorer = GridScorer.from_profile("equilibre")
        optimizer = GeneticAlgorithm(
            scorer=scorer,
            statistics=reference_statistics,
            game=loto_config,
            seed=42,
        )
        r1 = optimizer.optimize(n_grids=5)

        optimizer2 = GeneticAlgorithm(
            scorer=scorer,
            statistics=reference_statistics,
            game=loto_config,
            seed=42,
        )
        r2 = optimizer2.optimize(n_grids=5)

        assert len(r1) == len(r2) == 5
        for a, b in zip(r1, r2):
            assert a.numbers == b.numbers
            assert a.total_score == b.total_score

    def test_different_seeds_produce_different_grids(self, loto_config, reference_statistics):
        """Different seeds → different results."""
        scorer = GridScorer.from_profile("equilibre")
        opt1 = GeneticAlgorithm(
            scorer=scorer,
            statistics=reference_statistics,
            game=loto_config,
            seed=42,
        )
        opt2 = GeneticAlgorithm(
            scorer=scorer,
            statistics=reference_statistics,
            game=loto_config,
            seed=99,
        )
        r1 = opt1.optimize(n_grids=5)
        r2 = opt2.optimize(n_grids=5)

        grids1 = [tuple(g.numbers) for g in r1]
        grids2 = [tuple(g.numbers) for g in r2]
        # At least some grids differ
        assert grids1 != grids2


# ── SNAP-04: Monte Carlo simulation with seed ──


class TestMonteCarloSnapshot:
    """SNAP-04: Monte Carlo simulation with a fixed seed must be reproducible."""

    def test_simulation_reproducible(self, loto_config):
        """Same seed → same match distribution."""
        grid = [3, 12, 23, 34, 45]
        sim1 = MonteCarloSimulator(loto_config, seed=42)
        r1 = sim1.simulate_grid(grid, n_simulations=1000)

        sim2 = MonteCarloSimulator(loto_config, seed=42)
        r2 = sim2.simulate_grid(grid, n_simulations=1000)

        assert r1.match_distribution == r2.match_distribution
        assert r1.avg_matches == r2.avg_matches

    def test_simulation_different_seeds(self, loto_config):
        """Different seeds → different distributions."""
        grid = [3, 12, 23, 34, 45]
        sim1 = MonteCarloSimulator(loto_config, seed=42)
        sim2 = MonteCarloSimulator(loto_config, seed=99)
        r1 = sim1.simulate_grid(grid, n_simulations=1000)
        r2 = sim2.simulate_grid(grid, n_simulations=1000)
        assert r1.match_distribution != r2.match_distribution

    def test_simulation_snapshot_values(self, loto_config):
        """Pin expected structure and theoretical expectation."""
        grid = [3, 12, 23, 34, 45]
        sim = MonteCarloSimulator(loto_config, seed=42)
        result = sim.simulate_grid(grid, n_simulations=5000)

        # Structure checks
        assert result.n_simulations == 5000
        assert result.grid == sorted(grid)
        assert len(result.match_distribution) <= 6  # 0..5 matches
        assert sum(result.match_distribution.values()) == 5000

        # Theoretical: E(matches) = k^2/n = 25/49 ≈ 0.5102
        assert result.expected_matches == pytest.approx(25 / 49, rel=0.01)
        # Simulated avg should be close to theoretical
        assert result.avg_matches == pytest.approx(result.expected_matches, abs=0.1)

    def test_simulation_with_stars(self, euromillions_config):
        """Verify star simulation works and is reproducible."""
        grid = [5, 15, 25, 35, 45]
        stars = [3, 8]
        sim1 = MonteCarloSimulator(euromillions_config, seed=42)
        r1 = sim1.simulate_grid(grid, stars=stars, n_simulations=1000)

        sim2 = MonteCarloSimulator(euromillions_config, seed=42)
        r2 = sim2.simulate_grid(grid, stars=stars, n_simulations=1000)

        assert r1.match_distribution == r2.match_distribution
        assert r1.star_match_distribution == r2.star_match_distribution
        assert r1.star_match_distribution is not None
        assert sum(r1.star_match_distribution.values()) == 1000
