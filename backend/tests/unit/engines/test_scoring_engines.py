"""Tests for all 6 scoring criteria + GridScorer."""

import math

import numpy as np
import pytest

from app.core.game_definitions import GameConfig
from app.engines.scoring.balance_criterion import BalanceCriterion
from app.engines.scoring.cooccurrence_criterion import CooccurrenceCriterion
from app.engines.scoring.frequency_criterion import FrequencyCriterion
from app.engines.scoring.gap_criterion import GapCriterion
from app.engines.scoring.pattern_penalty import PatternPenalty
from app.engines.scoring.scorer import (
    PROFILES,
    GridScorer,
    ScoredResult,
    normalize_weights,
)
from app.engines.scoring.structure_criterion import StructureCriterion


# ── Fixtures ──


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
def small_config():
    """Small pool for easier manual validation."""
    return GameConfig(
        name="Mini",
        slug="mini",
        numbers_pool=10,
        numbers_drawn=3,
        min_number=1,
        max_number=10,
    )


@pytest.fixture
def sample_frequencies():
    """Frequency data matching engine output format (str keys from JSON)."""
    return {
        str(n): {
            "count": 10 + n,
            "relative": round((10 + n) / 100, 6),
            "ratio": round((10 + n) / 100 / (5 / 49), 4),
            "last_seen": max(0, 49 - n),
        }
        for n in range(1, 50)
    }


@pytest.fixture
def sample_gaps():
    """Gap data matching engine output format."""
    return {
        str(n): {
            "current_gap": n % 10,
            "max_gap": 20,
            "avg_gap": 10.0,
            "min_gap": 1,
            "median_gap": 9.0,
            "expected_gap": 9.8,
        }
        for n in range(1, 50)
    }


@pytest.fixture
def sample_cooccurrences():
    """Cooccurrence data matching engine output format."""
    pairs = {}
    for i in range(1, 50):
        for j in range(i + 1, 50):
            pairs[f"{i}-{j}"] = {
                "count": i + j,
                "expected": 5.0,
                "affinity": round((i + j) / 5.0, 4),
            }
    return {
        "pairs": pairs,
        "expected_pair_count": 5.0,
        "matrix_shape": [49, 49],
    }


@pytest.fixture
def sample_statistics(sample_frequencies, sample_gaps, sample_cooccurrences):
    """Complete statistics dict as consumed by GridScorer."""
    return {
        "frequency": sample_frequencies,
        "gaps": sample_gaps,
        "cooccurrence": sample_cooccurrences,
    }


# ── FrequencyCriterion ──


class TestFrequencyCriterion:
    def setup_method(self):
        self.criterion = FrequencyCriterion()

    def test_name(self):
        assert self.criterion.get_name() == "frequency"

    def test_returns_float_in_range(self, loto_config, sample_frequencies):
        score = self.criterion.compute(
            [5, 12, 23, 34, 47], loto_config, frequencies=sample_frequencies
        )
        assert 0 <= score <= 1

    def test_high_frequency_numbers_score_higher(self, loto_config, sample_frequencies):
        high_nums = [45, 46, 47, 48, 49]  # Higher ratios
        low_nums = [1, 2, 3, 4, 5]  # Lower ratios
        high_score = self.criterion.compute(
            high_nums, loto_config, frequencies=sample_frequencies
        )
        low_score = self.criterion.compute(
            low_nums, loto_config, frequencies=sample_frequencies
        )
        assert high_score > low_score

    def test_empty_frequencies(self, loto_config):
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, frequencies={})
        assert score == 0.5

    def test_all_same_ratio(self, loto_config):
        flat = {
            str(n): {"count": 10, "relative": 0.1, "ratio": 1.0, "last_seen": 0}
            for n in range(1, 50)
        }
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, frequencies=flat)
        # All ratios equal → min_r == max_r → range_r = 1 → normalized = 0
        assert score == 0.0


# ── GapCriterion ──


class TestGapCriterion:
    def setup_method(self):
        self.criterion = GapCriterion(sensitivity=3.0)

    def test_name(self):
        assert self.criterion.get_name() == "gap"

    def test_returns_float_in_range(self, loto_config, sample_gaps):
        score = self.criterion.compute(
            [5, 12, 23, 34, 47], loto_config, gaps=sample_gaps
        )
        assert 0 <= score <= 1

    def test_overdue_numbers_score_high(self, loto_config):
        gaps = {
            str(n): {"current_gap": 50, "avg_gap": 10.0}
            for n in range(1, 50)
        }
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, gaps=gaps)
        # current >> avg → ratio = 4 → sigmoid(12) ≈ 1
        assert score > 0.9

    def test_recent_numbers_score_low(self, loto_config):
        gaps = {
            str(n): {"current_gap": 0, "avg_gap": 10.0}
            for n in range(1, 50)
        }
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, gaps=gaps)
        # current << avg → ratio = -1 → sigmoid(-3) ≈ 0.047
        assert score < 0.1

    def test_zero_avg_returns_neutral(self, loto_config):
        gaps = {str(n): {"current_gap": 5, "avg_gap": 0} for n in range(1, 50)}
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, gaps=gaps)
        assert score == 0.5

    def test_missing_number_returns_neutral(self, loto_config):
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config, gaps={})
        assert score == 0.5

    def test_custom_sensitivity(self, loto_config):
        gaps = {str(n): {"current_gap": 15, "avg_gap": 10.0} for n in range(1, 50)}
        low_sens = GapCriterion(sensitivity=1.0)
        high_sens = GapCriterion(sensitivity=10.0)
        s_low = low_sens.compute([1, 2, 3, 4, 5], loto_config, gaps=gaps)
        s_high = high_sens.compute([1, 2, 3, 4, 5], loto_config, gaps=gaps)
        # Higher sensitivity → more extreme sigmoid → higher score for overdue
        assert s_high > s_low


# ── CooccurrenceCriterion ──


class TestCooccurrenceCriterion:
    def setup_method(self):
        self.criterion = CooccurrenceCriterion()

    def test_name(self):
        assert self.criterion.get_name() == "cooccurrence"

    def test_returns_float_in_range(self, loto_config, sample_cooccurrences):
        score = self.criterion.compute(
            [5, 12, 23, 34, 47], loto_config, cooccurrences=sample_cooccurrences
        )
        assert 0 <= score <= 1

    def test_high_affinity_pairs_score_higher(self, loto_config, sample_cooccurrences):
        # Pairs with high sums (high i+j) have higher affinity in our fixture
        high_pair_grid = [45, 46, 47, 48, 49]
        low_pair_grid = [1, 2, 3, 4, 5]
        high_score = self.criterion.compute(
            high_pair_grid, loto_config, cooccurrences=sample_cooccurrences
        )
        low_score = self.criterion.compute(
            low_pair_grid, loto_config, cooccurrences=sample_cooccurrences
        )
        assert high_score > low_score

    def test_empty_pairs(self, loto_config):
        score = self.criterion.compute(
            [1, 2, 3, 4, 5], loto_config, cooccurrences={"pairs": {}}
        )
        assert score == 0.5

    def test_single_number_grid(self, loto_config, sample_cooccurrences):
        score = self.criterion.compute(
            [5], loto_config, cooccurrences=sample_cooccurrences
        )
        assert score == 0.5  # No pairs → default


# ── StructureCriterion ──


class TestStructureCriterion:
    def setup_method(self):
        self.criterion = StructureCriterion()

    def test_name(self):
        assert self.criterion.get_name() == "structure"

    def test_returns_float_in_range(self, loto_config):
        score = self.criterion.compute([5, 12, 23, 34, 47], loto_config)
        assert 0 <= score <= 1

    def test_well_spread_grid_scores_high(self, loto_config):
        # Good: 2 even + 3 odd, spread across decades, balanced low/high
        score = self.criterion.compute([3, 14, 25, 36, 47], loto_config)
        assert score > 0.5

    def test_all_same_decade_scores_low(self, loto_config):
        # All in decade 0 (1-10), all odd
        score = self.criterion.compute([1, 3, 5, 7, 9], loto_config)
        assert score < 0.5

    def test_perfect_balance(self, small_config):
        # 3 numbers from 1-10: one low, one mid, one high
        score = self.criterion.compute([2, 5, 9], small_config)
        assert score > 0.5


# ── BalanceCriterion ──


class TestBalanceCriterion:
    def setup_method(self):
        self.criterion = BalanceCriterion()

    def test_name(self):
        assert self.criterion.get_name() == "balance"

    def test_returns_float_in_range(self, loto_config):
        score = self.criterion.compute([5, 12, 23, 34, 47], loto_config)
        assert 0 <= score <= 1

    def test_uniform_spread_scores_high(self, loto_config):
        # Evenly spaced: 1, 13, 25, 37, 49
        score = self.criterion.compute([1, 13, 25, 37, 49], loto_config)
        assert score > 0.7

    def test_clustered_scores_low(self, loto_config):
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config)
        # All clustered at the bottom → large deviation
        assert score < 0.5

    def test_score_clamped_to_01(self, loto_config):
        score = self.criterion.compute([49, 48, 47, 46, 45], loto_config)
        assert 0 <= score <= 1


# ── PatternPenalty ──


class TestPatternPenalty:
    def setup_method(self):
        self.criterion = PatternPenalty()

    def test_name(self):
        assert self.criterion.get_name() == "pattern_penalty"

    def test_no_pattern_zero_penalty(self, loto_config):
        # Random-looking grid with no obvious patterns
        score = self.criterion.compute([3, 17, 28, 35, 44], loto_config)
        assert score == 0.0

    def test_arithmetic_sequence_max_penalty(self, loto_config):
        # 5, 10, 15, 20, 25 → arithmetic (step=5) + all multiples of 5
        score = self.criterion.compute([5, 10, 15, 20, 25], loto_config)
        assert score == 1.0  # Capped at 1.0

    def test_consecutive_numbers_penalty(self, loto_config):
        score = self.criterion.compute([10, 11, 12, 13, 30], loto_config)
        assert score > 0  # consecutive ≥ 3

    def test_all_even_penalty(self, loto_config):
        score = self.criterion.compute([2, 14, 26, 38, 48], loto_config)
        assert score >= 0.4  # All even → 0.4

    def test_all_odd_penalty(self, loto_config):
        score = self.criterion.compute([1, 13, 25, 37, 49], loto_config)
        assert score >= 0.4

    def test_same_decade_penalty(self, loto_config):
        score = self.criterion.compute([1, 3, 5, 7, 9], loto_config)
        # Same decade + all odd + narrow span → multiple penalties
        assert score > 0.4

    def test_narrow_span_penalty(self, loto_config):
        score = self.criterion.compute([20, 22, 25, 28, 30], loto_config)
        # Span = 10 < 15 → penalty of 0.3 * (1 - 10/15) = 0.1
        assert score > 0

    def test_penalty_capped_at_one(self, loto_config):
        # Worst case: consecutive + same decade + all odd + narrow span + arithmetic
        score = self.criterion.compute([1, 2, 3, 4, 5], loto_config)
        assert score <= 1.0


# ── GridScorer ──


class TestGridScorer:
    def test_default_weights(self):
        scorer = GridScorer()
        assert scorer.weights == PROFILES["equilibre"]

    def test_from_profile(self):
        for name in PROFILES:
            scorer = GridScorer.from_profile(name)
            assert scorer.weights == PROFILES[name]

    def test_from_invalid_profile(self):
        with pytest.raises(ValueError, match="Unknown profile"):
            GridScorer.from_profile("nonexistent")

    def test_score_returns_scored_result(self, loto_config, sample_statistics):
        scorer = GridScorer()
        result = scorer.score([5, 12, 23, 34, 47], sample_statistics, loto_config)
        assert isinstance(result, ScoredResult)
        assert 0 <= result.total_score <= 1
        assert set(result.score_breakdown.keys()) == {
            "frequency", "gap", "cooccurrence", "structure", "balance", "pattern_penalty"
        }

    def test_all_breakdown_scores_in_range(self, loto_config, sample_statistics):
        scorer = GridScorer()
        result = scorer.score([5, 12, 23, 34, 47], sample_statistics, loto_config)
        for key, val in result.score_breakdown.items():
            assert 0 <= val <= 1, f"{key} = {val} out of range"

    def test_different_profiles_give_different_scores(self, loto_config, sample_statistics):
        grid = [5, 12, 23, 34, 47]
        scores = set()
        for name in PROFILES:
            scorer = GridScorer.from_profile(name)
            result = scorer.score(grid, sample_statistics, loto_config)
            scores.add(result.total_score)
        # At least some profiles should give different scores
        assert len(scores) > 1

    def test_custom_weights(self, loto_config, sample_statistics):
        custom = {
            "frequency": 1.0,
            "gap": 0.0,
            "cooccurrence": 0.0,
            "structure": 0.0,
            "balance": 0.0,
            "pattern_penalty": 0.0,
        }
        scorer = GridScorer(weights=custom)
        result = scorer.score([5, 12, 23, 34, 47], sample_statistics, loto_config)
        assert 0 <= result.total_score <= 1

    def test_numbers_sorted_in_result(self, loto_config, sample_statistics):
        scorer = GridScorer()
        result = scorer.score([47, 5, 34, 12, 23], sample_statistics, loto_config)
        assert result.numbers == [5, 12, 23, 34, 47]

    def test_score_with_stars(self, loto_config, sample_statistics):
        scorer = GridScorer()
        result = scorer.score_with_stars(
            [5, 12, 23, 34, 47], [3], sample_statistics, loto_config
        )
        assert result.stars == [3]
        assert result.star_score is not None
        assert 0 <= result.total_score <= 1

    def test_score_with_stars_no_star_data(self, loto_config, sample_statistics):
        scorer = GridScorer()
        result = scorer.score_with_stars(
            [5, 12, 23, 34, 47], [3], sample_statistics, loto_config
        )
        # No star_frequency/star_gaps in statistics → star_score defaults to 0.5
        assert result.star_score == 0.5


# ── normalize_weights ──


class TestNormalizeWeights:
    def test_default_weights_are_valid(self):
        w = normalize_weights(PROFILES["equilibre"])
        main_sum = sum(v for k, v in w.items() if k != "pattern_penalty")
        assert abs(main_sum - 1.0) < 0.001

    def test_custom_weights_normalized(self):
        raw = {
            "frequency": 2.0,
            "gap": 2.0,
            "cooccurrence": 1.0,
            "structure": 1.0,
            "balance": 2.0,
            "pattern_penalty": 0.5,
        }
        w = normalize_weights(raw)
        main_sum = sum(v for k, v in w.items() if k != "pattern_penalty")
        assert abs(main_sum - 1.0) < 0.001

    def test_zero_weights(self):
        raw = {
            "frequency": 0,
            "gap": 0,
            "cooccurrence": 0,
            "structure": 0,
            "balance": 0,
            "pattern_penalty": 0,
        }
        w = normalize_weights(raw)
        # Should not crash (total_main fallback to 1.0)
        assert isinstance(w, dict)
