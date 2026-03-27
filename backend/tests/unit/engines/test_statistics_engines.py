"""Tests for all 7 statistical engines."""

import networkx as nx
import numpy as np
import pytest
from scipy.stats import beta as beta_dist

from app.core.game_definitions import GameConfig
from app.engines.statistics.bayesian import BayesianEngine
from app.engines.statistics.cooccurrence import CooccurrenceEngine
from app.engines.statistics.distribution import DistributionEngine
from app.engines.statistics.frequency import FrequencyEngine
from app.engines.statistics.gap import GapEngine
from app.engines.statistics.graph import GraphEngine
from app.engines.statistics.temporal import TemporalEngine


# ── Fixtures ──


@pytest.fixture
def loto_config() -> GameConfig:
    return GameConfig(
        name="Loto FDJ",
        slug="loto-fdj",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
    )


@pytest.fixture
def small_config() -> GameConfig:
    """Small game for easier manual verification."""
    return GameConfig(
        name="Mini Loto",
        slug="mini-loto",
        numbers_pool=10,
        numbers_drawn=3,
        min_number=1,
        max_number=10,
    )


@pytest.fixture
def small_draws() -> np.ndarray:
    """10 draws of 3 numbers from 1-10 for manual verification."""
    return np.array([
        [1, 3, 7],
        [2, 5, 9],
        [1, 4, 8],
        [3, 6, 10],
        [1, 5, 7],
        [2, 3, 9],
        [4, 7, 10],
        [1, 6, 8],
        [3, 5, 9],
        [2, 7, 10],
    ])


@pytest.fixture
def loto_draws() -> np.ndarray:
    """10 Loto FDJ draws from sample data."""
    return np.array([
        [3, 12, 25, 37, 44],
        [1, 8, 19, 33, 48],
        [5, 14, 22, 36, 41],
        [2, 17, 28, 39, 45],
        [7, 11, 24, 31, 49],
        [3, 9, 18, 35, 42],
        [6, 15, 27, 38, 46],
        [4, 13, 23, 34, 47],
        [10, 16, 29, 40, 43],
        [1, 20, 26, 32, 44],
    ])


# ══════════════════════════════════════════════════════════════
#  FrequencyEngine
# ══════════════════════════════════════════════════════════════


class TestFrequencyEngine:
    def setup_method(self):
        self.engine = FrequencyEngine()

    def test_name(self):
        assert self.engine.get_name() == "frequency"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result == {}

    def test_all_numbers_present(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert len(result) == 10  # numbers 1-10
        for num in range(1, 11):
            assert num in result
            assert "count" in result[num]
            assert "relative" in result[num]
            assert "ratio" in result[num]
            assert "last_seen" in result[num]

    def test_frequency_count_manual(self, small_draws, small_config):
        """Number 1 appears in draws 0,2,4,7 → count=4."""
        result = self.engine.compute(small_draws, small_config)
        assert result[1]["count"] == 4

    def test_frequency_relative(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # 4 appearances in 10 draws → relative = 0.4
        assert result[1]["relative"] == 0.4

    def test_frequency_ratio(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # theoretical_p = 3/10 = 0.3, relative = 0.4
        # ratio = 0.4 / 0.3 = 1.3333
        assert abs(result[1]["ratio"] - 1.3333) < 0.01

    def test_last_seen(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # Number 1 last appeared at index 7, n_draws=10
        # last_seen = 10 - 1 - 7 = 2
        assert result[1]["last_seen"] == 2

    def test_total_counts(self, small_draws, small_config):
        """Total count across all numbers = n_draws * numbers_drawn = 10*3 = 30."""
        result = self.engine.compute(small_draws, small_config)
        total = sum(r["count"] for r in result.values())
        assert total == 30

    def test_loto_draws(self, loto_draws, loto_config):
        result = self.engine.compute(loto_draws, loto_config)
        assert len(result) == 49
        # Total appearances = 10 * 5 = 50
        total = sum(r["count"] for r in result.values())
        assert total == 50


# ══════════════════════════════════════════════════════════════
#  GapEngine
# ══════════════════════════════════════════════════════════════


class TestGapEngine:
    def setup_method(self):
        self.engine = GapEngine()

    def test_name(self):
        assert self.engine.get_name() == "gaps"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result == {}

    def test_all_numbers_present(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert len(result) == 10
        for num in range(1, 11):
            assert "current_gap" in result[num]
            assert "max_gap" in result[num]
            assert "avg_gap" in result[num]
            assert "min_gap" in result[num]

    def test_current_gap_manual(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # Number 1 last at index 7, n_draws=10 → current_gap = 10-1-7 = 2
        assert result[1]["current_gap"] == 2

    def test_expected_gap(self, small_config, small_draws):
        result = self.engine.compute(small_draws, small_config)
        # 10/3 = 3.33
        assert abs(result[1]["expected_gap"] - 3.33) < 0.01

    def test_never_appeared(self, small_config):
        """A number that never appeared has gap = n_draws."""
        draws = np.array([[1, 2, 3], [1, 2, 4]])
        result = self.engine.compute(draws, small_config)
        # Number 10 never appeared
        assert result[10]["current_gap"] == 2
        assert result[10]["max_gap"] == 2

    def test_gap_range_valid(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        for num, data in result.items():
            assert data["min_gap"] <= data["avg_gap"] <= data["max_gap"]
            assert data["current_gap"] >= 0

    def test_loto_draws(self, loto_draws, loto_config):
        result = self.engine.compute(loto_draws, loto_config)
        assert len(result) == 49


# ══════════════════════════════════════════════════════════════
#  CooccurrenceEngine
# ══════════════════════════════════════════════════════════════


class TestCooccurrenceEngine:
    def setup_method(self):
        self.engine = CooccurrenceEngine()

    def test_name(self):
        assert self.engine.get_name() == "cooccurrence"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result["pairs"] == {}

    def test_output_structure(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert "pairs" in result
        assert "expected_pair_count" in result
        assert "matrix_shape" in result
        assert result["matrix_shape"] == [10, 10]

    def test_pair_count_manual(self, small_draws, small_config):
        """Numbers (1,7) co-appear in draws 0,4 → count = 2."""
        result = self.engine.compute(small_draws, small_config)
        pair_key = "1-7"
        assert result["pairs"][pair_key]["count"] == 2

    def test_expected_pair_count(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # Expected = N * k*(k-1) / (n*(n-1)) = 10 * 3*2 / (10*9) = 60/90 = 0.67
        assert abs(result["expected_pair_count"] - 0.67) < 0.01

    def test_symmetric_pairs(self, small_draws, small_config):
        """Only i<j pairs should exist."""
        result = self.engine.compute(small_draws, small_config)
        for key in result["pairs"]:
            parts = key.split("-")
            assert int(parts[0]) < int(parts[1])

    def test_affinity_positive(self, small_draws, small_config):
        """Pairs that co-occur should have positive affinity."""
        result = self.engine.compute(small_draws, small_config)
        pair = result["pairs"]["1-7"]
        assert pair["affinity"] > 0

    def test_get_cooccurrence_matrix(self, small_draws, small_config):
        matrix = self.engine.get_cooccurrence_matrix(small_draws, small_config)
        assert matrix.shape == (10, 10)
        # Diagonal should be the appearance count of each number
        # Number 1 appears 4 times → matrix[0,0]=4
        assert matrix[0, 0] == 4

    def test_loto_draws(self, loto_draws, loto_config):
        result = self.engine.compute(loto_draws, loto_config)
        n_pairs = 49 * 48 // 2
        assert len(result["pairs"]) == n_pairs


# ══════════════════════════════════════════════════════════════
#  TemporalEngine
# ══════════════════════════════════════════════════════════════


class TestTemporalEngine:
    def setup_method(self):
        self.engine = TemporalEngine()

    def test_name(self):
        assert self.engine.get_name() == "temporal"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result == {"windows": []}

    def test_too_few_draws(self, small_config):
        """With 10 draws, no window of 20+ fits → empty windows."""
        draws = np.random.default_rng(42).choice(
            range(1, 11), size=(10, 3), replace=True
        )
        result = self.engine.compute(draws, small_config)
        assert result["windows"] == []

    def test_sufficient_draws(self, small_config):
        """With 25 draws, window of 20 fits."""
        rng = np.random.default_rng(42)
        draws = np.column_stack([
            rng.choice(range(1, 11), size=25) for _ in range(3)
        ])
        result = self.engine.compute(draws, small_config)
        assert len(result["windows"]) == 1
        assert result["windows"][0]["window_size"] == 20

    def test_hot_cold_structure(self, small_config):
        rng = np.random.default_rng(42)
        draws = np.column_stack([
            rng.choice(range(1, 11), size=25) for _ in range(3)
        ])
        result = self.engine.compute(draws, small_config)
        if result["windows"]:
            w = result["windows"][0]
            assert "hot_numbers" in w
            assert "cold_numbers" in w
            for entry in w["hot_numbers"]:
                assert entry["delta"] > 0.02

    def test_momentum_with_multiple_windows(self, small_config):
        """With 250 draws, windows 20,50,100,200 all fit → momentum computed."""
        rng = np.random.default_rng(42)
        draws = np.column_stack([
            rng.choice(range(1, 11), size=250) for _ in range(3)
        ])
        result = self.engine.compute(draws, small_config)
        assert len(result["windows"]) == 4
        assert "momentum" in result
        assert len(result["momentum"]) == 10  # 10 numbers


# ══════════════════════════════════════════════════════════════
#  DistributionEngine
# ══════════════════════════════════════════════════════════════


class TestDistributionEngine:
    def setup_method(self):
        self.engine = DistributionEngine()

    def test_name(self):
        assert self.engine.get_name() == "distribution"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result == {}

    def test_output_structure(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert "entropy" in result
        assert "max_entropy" in result
        assert "uniformity_score" in result
        assert "chi2_statistic" in result
        assert "chi2_pvalue" in result
        assert "is_uniform" in result
        assert "sum_stats" in result
        assert "even_odd_distribution" in result
        assert "decades" in result

    def test_entropy_bounds(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert 0 <= result["entropy"] <= result["max_entropy"]
        assert 0 <= result["uniformity_score"] <= 1

    def test_chi2_pvalue_range(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert 0 <= result["chi2_pvalue"] <= 1

    def test_sum_stats(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        ss = result["sum_stats"]
        assert ss["min"] <= ss["mean"] <= ss["max"]
        assert ss["std"] >= 0

    def test_even_odd(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        eo = result["even_odd_distribution"]
        assert abs(eo["mean_even"] + eo["mean_odd"] - 3) < 0.01  # k=3

    def test_decades(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        # All numbers 1-10 fit in one decade "1-10"
        assert "1-10" in result["decades"]

    def test_uniform_draws(self, small_config):
        """Perfectly uniform draws should have high uniformity score."""
        # Each number appears exactly 3 times in 10 draws of 3
        draws = np.array([
            [1, 2, 3], [4, 5, 6], [7, 8, 9],
            [10, 1, 2], [3, 4, 5], [6, 7, 8],
            [9, 10, 1], [2, 3, 4], [5, 6, 7],
            [8, 9, 10],
        ])
        result = self.engine.compute(draws, small_config)
        assert result["uniformity_score"] > 0.95

    def test_loto_draws(self, loto_draws, loto_config):
        result = self.engine.compute(loto_draws, loto_config)
        assert result["max_entropy"] == round(float(np.log2(49)), 4)


# ══════════════════════════════════════════════════════════════
#  BayesianEngine
# ══════════════════════════════════════════════════════════════


class TestBayesianEngine:
    def setup_method(self):
        self.engine = BayesianEngine()

    def test_name(self):
        assert self.engine.get_name() == "bayesian"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result == {}

    def test_output_structure(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert len(result) == 10
        for num in range(1, 11):
            item = result[num]
            assert "alpha" in item
            assert "beta" in item
            assert "posterior_mean" in item
            assert "ci_95_low" in item
            assert "ci_95_high" in item
            assert "ci_width" in item

    def test_posterior_mean_range(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        for num, item in result.items():
            assert 0 < item["posterior_mean"] < 1

    def test_alpha_beta_values(self, small_draws, small_config):
        """Number 1 appears 4 times in 10 draws.
        alpha = 0.5 + 4 = 4.5
        beta = 0.5 + (10 - 4) = 6.5
        """
        result = self.engine.compute(small_draws, small_config)
        assert result[1]["alpha"] == 4.5
        assert result[1]["beta"] == 6.5

    def test_credible_interval_contains_mean(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        for num, item in result.items():
            assert item["ci_95_low"] <= item["posterior_mean"] <= item["ci_95_high"]

    def test_credible_interval_width(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        for num, item in result.items():
            assert item["ci_width"] > 0
            assert abs(item["ci_width"] - (item["ci_95_high"] - item["ci_95_low"])) < 1e-4

    def test_more_data_narrows_ci(self, small_config):
        """More draws should narrow the credible interval."""
        rng = np.random.default_rng(42)
        draws_small = np.column_stack([rng.choice(range(1, 11), size=20) for _ in range(3)])
        draws_large = np.column_stack([rng.choice(range(1, 11), size=200) for _ in range(3)])

        result_small = self.engine.compute(draws_small, small_config)
        result_large = self.engine.compute(draws_large, small_config)

        avg_width_small = np.mean([v["ci_width"] for v in result_small.values()])
        avg_width_large = np.mean([v["ci_width"] for v in result_large.values()])
        assert avg_width_large < avg_width_small


# ══════════════════════════════════════════════════════════════
#  GraphEngine
# ══════════════════════════════════════════════════════════════


class TestGraphEngine:
    def setup_method(self):
        self.engine = GraphEngine()

    def test_name(self):
        assert self.engine.get_name() == "graph"

    def test_empty_draws(self, loto_config):
        result = self.engine.compute(np.array([]).reshape(0, 5), loto_config)
        assert result["communities"] == []
        assert result["density"] == 0.0

    def test_output_structure(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert "communities" in result
        assert "centrality" in result
        assert "density" in result
        assert "clustering_coefficient" in result

    def test_centrality_structure(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert len(result["centrality"]) == 10
        for num, data in result["centrality"].items():
            assert "degree" in data
            assert "betweenness" in data
            assert "eigenvector" in data
            assert "community" in data

    def test_density_range(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        assert 0 <= result["density"] <= 1

    def test_communities_cover_all_numbers(self, small_draws, small_config):
        result = self.engine.compute(small_draws, small_config)
        all_nums = set()
        for comm in result["communities"]:
            all_nums.update(comm)
        # All numbers 1-10 should be in some community
        for num in range(1, 11):
            assert num in all_nums

    def test_loto_draws(self, loto_draws, loto_config):
        result = self.engine.compute(loto_draws, loto_config)
        assert len(result["centrality"]) == 49
        assert result["density"] >= 0

    def test_eigenvector_convergence_failure(self, small_draws, small_config):
        """When eigenvector_centrality fails, fallback to 0.0 for all nodes."""
        from unittest.mock import patch

        with patch(
            "app.engines.statistics.graph.nx.eigenvector_centrality",
            side_effect=nx.PowerIterationFailedConvergence(1000),
        ):
            result = self.engine.compute(small_draws, small_config)
        for data in result["centrality"].values():
            assert data["eigenvector"] == 0.0

    def test_louvain_failure(self, small_draws, small_config):
        """When louvain_communities raises, communities should be empty."""
        from unittest.mock import patch

        with patch(
            "app.engines.statistics.graph.louvain_communities",
            side_effect=RuntimeError("louvain failed"),
        ):
            result = self.engine.compute(small_draws, small_config)
        assert result["communities"] == []
        for data in result["centrality"].values():
            assert data["community"] == -1
