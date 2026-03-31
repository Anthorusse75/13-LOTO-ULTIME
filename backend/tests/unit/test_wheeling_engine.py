"""Tests for the wheeling engine modules — greedy cover, coverage, cost, gains."""

import pytest

from app.engines.wheeling.coverage import (
    coverage_rate,
    full_wheel_size,
    reduction_rate,
    total_t_combinations,
)
from app.engines.wheeling.cost_estimator import estimate_cost, estimate_grid_count
from app.engines.wheeling.engine import WheelingEngine
from app.engines.wheeling.gain_analyzer import analyze_gains
from app.engines.wheeling.greedy_cover import greedy_cover
from app.core.game_definitions import GameConfig


# ── Fixtures ──

LOTO_CONFIG = GameConfig(
    name="Loto FDJ",
    slug="loto_fdj",
    numbers_pool=49,
    numbers_drawn=5,
    min_number=1,
    max_number=49,
    stars_pool=10,
    stars_drawn=1,
    star_name="chance",
    grid_price=2.20,
)

EUROMILLIONS_CONFIG = GameConfig(
    name="EuroMillions",
    slug="euromillions",
    numbers_pool=50,
    numbers_drawn=5,
    min_number=1,
    max_number=50,
    stars_pool=12,
    stars_drawn=2,
    star_name="étoile",
    grid_price=2.50,
)

SAMPLE_PRIZE_TIERS = [
    {"rank": 1, "name": "5 bons", "match_numbers": 5, "match_stars": 0, "avg_prize": 1_000_000, "probability": 0.0000001},
    {"rank": 2, "name": "4 bons", "match_numbers": 4, "match_stars": 0, "avg_prize": 1_000, "probability": 0.0001},
    {"rank": 3, "name": "3 bons", "match_numbers": 3, "match_stars": 0, "avg_prize": 10, "probability": 0.01},
]


# ── greedy_cover tests ──


class TestGreedyCover:
    def test_small_cover_n8_k5_t2(self):
        """n=8, k=5, t=2 → should cover all 2-subsets."""
        numbers = list(range(1, 9))
        grids = greedy_cover(numbers, k=5, t=2)
        assert len(grids) > 0
        # Verify every 2-subset is covered
        from itertools import combinations
        all_pairs = set(combinations(sorted(numbers), 2))
        covered = set()
        for g in grids:
            covered.update(combinations(g, 2))
        assert covered == all_pairs

    def test_cover_n10_k5_t3(self):
        """n=10, k=5, t=3 → should cover all 3-subsets with reasonable grid count."""
        numbers = list(range(1, 11))
        grids = greedy_cover(numbers, k=5, t=3)
        # Greedy approximation: theoretical min ~10, greedy may produce up to ~25
        assert len(grids) <= 25
        from itertools import combinations
        all_triples = set(combinations(sorted(numbers), 3))
        covered = set()
        for g in grids:
            covered.update(combinations(g, 3))
        assert covered == all_triples

    def test_n_equals_k(self):
        """When n == k, only one grid is possible."""
        numbers = [1, 2, 3, 4, 5]
        grids = greedy_cover(numbers, k=5, t=3)
        assert len(grids) == 1
        assert grids[0] == (1, 2, 3, 4, 5)

    def test_invalid_n_less_than_k(self):
        with pytest.raises(ValueError, match="at least"):
            greedy_cover([1, 2, 3], k=5, t=2)

    def test_invalid_t_out_of_range(self):
        with pytest.raises(ValueError, match="Guarantee t"):
            greedy_cover([1, 2, 3, 4, 5, 6], k=5, t=6)

    def test_invalid_t_below_2(self):
        with pytest.raises(ValueError, match="Guarantee t"):
            greedy_cover([1, 2, 3, 4, 5, 6], k=5, t=1)


# ── coverage tests ──


class TestCoverage:
    def test_full_coverage(self):
        numbers = list(range(1, 9))
        grids = greedy_cover(numbers, k=5, t=2)
        rate = coverage_rate(grids, numbers, t=2)
        assert rate == 1.0

    def test_total_t_combinations(self):
        assert total_t_combinations(10, 3) == 120

    def test_full_wheel_size(self):
        assert full_wheel_size(10, 5) == 252

    def test_reduction_rate(self):
        rate = reduction_rate(10, 10, 5)
        # 10 grids vs 252 full wheel → (1 - 10/252) × 100
        assert rate == pytest.approx((1 - 10 / 252) * 100, abs=0.1)


# ── cost estimator tests ──


class TestCostEstimator:
    def test_estimate_cost(self):
        assert estimate_cost(10, 2.20) == 22.0

    def test_estimate_cost_euromillions(self):
        assert estimate_cost(5, 2.50) == 12.5

    def test_estimate_grid_count(self):
        count = estimate_grid_count(10, 5, 3)
        assert count >= 1
        # Lower bound: C(10,3)/C(5,3) = 120/10 = 12
        assert count >= 12


# ── gain analyzer tests ──


class TestGainAnalyzer:
    def test_basic_gain_scenarios(self):
        numbers = list(range(1, 9))
        grids = greedy_cover(numbers, k=5, t=2)
        scenarios = analyze_gains(grids, numbers, SAMPLE_PRIZE_TIERS, k=5)
        assert len(scenarios) == 3
        # All scenarios should have non-negative values
        for s in scenarios:
            assert s.matching_grids_best >= 0
            assert s.potential_gain_best >= 0

    def test_rank3_has_matches(self):
        """With t=2 coverage, rank 3 (match 3) should see some grids matching."""
        numbers = list(range(1, 9))
        grids = greedy_cover(numbers, k=5, t=2)
        scenarios = analyze_gains(grids, numbers, SAMPLE_PRIZE_TIERS, k=5)
        rank3 = next(s for s in scenarios if s.rank == 3)
        assert rank3.matching_grids_best > 0


# ── engine tests ──


class TestWheelingEngine:
    def test_preview(self):
        engine = WheelingEngine(LOTO_CONFIG)
        result = engine.preview([1, 2, 3, 4, 5, 6, 7, 8], stars=None, guarantee=2)
        assert result.estimated_grid_count >= 1
        assert result.estimated_cost > 0
        assert result.full_wheel_size == 56  # C(8,5)
        assert result.total_t_combinations == 28  # C(8,2)

    def test_generate_without_stars(self):
        engine = WheelingEngine(LOTO_CONFIG)
        result = engine.generate([1, 2, 3, 4, 5, 6, 7, 8], stars=None, guarantee=2)
        assert result.grid_count > 0
        assert result.coverage_rate == 1.0
        assert result.total_cost > 0
        assert result.computation_time_ms >= 0
        # All grids should have no stars
        for g in result.grids:
            assert g.stars is None

    def test_generate_with_stars_loto(self):
        """Loto FDJ: stars distributed cyclically."""
        engine = WheelingEngine(LOTO_CONFIG)
        result = engine.generate(
            [1, 2, 3, 4, 5, 6, 7], stars=[1, 3, 5], guarantee=2
        )
        assert result.grid_count > 0
        for g in result.grids:
            assert g.stars is not None
            assert len(g.stars) == 1  # Loto draws 1 chance

    def test_generate_with_stars_euromillions(self):
        """EuroMillions: star combos expand grids."""
        engine = WheelingEngine(EUROMILLIONS_CONFIG)
        result = engine.generate(
            [1, 2, 3, 4, 5, 6, 7], stars=[1, 2, 3], guarantee=2
        )
        assert result.grid_count > 0
        for g in result.grids:
            assert g.stars is not None
            assert len(g.stars) == 2  # EuroMillions draws 2 stars

    def test_generate_with_gain_scenarios(self):
        engine = WheelingEngine(LOTO_CONFIG)
        result = engine.generate(
            [1, 2, 3, 4, 5, 6, 7, 8],
            stars=None,
            guarantee=2,
            prize_tiers=SAMPLE_PRIZE_TIERS,
        )
        assert len(result.gain_scenarios) == 3

    def test_number_distribution(self):
        engine = WheelingEngine(LOTO_CONFIG)
        result = engine.generate([1, 2, 3, 4, 5, 6, 7, 8], stars=None, guarantee=2)
        assert len(result.number_distribution) > 0
        for num in [1, 2, 3, 4, 5, 6, 7, 8]:
            assert num in result.number_distribution
            assert result.number_distribution[num] >= 1
