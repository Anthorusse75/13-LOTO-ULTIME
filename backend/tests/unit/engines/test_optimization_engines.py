"""Tests for optimization engines — meta-heuristics + portfolio."""

import pytest

from app.core.game_definitions import GameConfig
from app.engines.optimization.genetic import GeneticAlgorithm
from app.engines.optimization.hill_climbing import HillClimbing
from app.engines.optimization.method_selector import select_method
from app.engines.optimization.multi_objective import MultiObjectiveOptimizer
from app.engines.optimization.portfolio import (
    STRATEGY_WEIGHTS,
    PortfolioOptimizer,
    PortfolioResult,
)
from app.engines.optimization.simulated_annealing import SimulatedAnnealing
from app.engines.optimization.tabu import TabuSearch
from app.engines.scoring.scorer import GridScorer, ScoredResult

# ── Fixtures ──


@pytest.fixture
def small_config():
    """Small game config for fast tests (10 choose 3)."""
    return GameConfig(
        name="Mini",
        slug="mini",
        numbers_pool=10,
        numbers_drawn=3,
        min_number=1,
        max_number=10,
    )


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
def sample_statistics():
    """Minimal statistics dict for scoring."""
    frequencies = {
        str(n): {"count": 10, "relative": 0.1, "ratio": 1.0, "last_seen": 0} for n in range(1, 50)
    }
    gaps = {
        str(n): {
            "current_gap": 5,
            "avg_gap": 10.0,
            "max_gap": 20,
            "min_gap": 1,
            "median_gap": 9.0,
            "expected_gap": 9.8,
        }
        for n in range(1, 50)
    }
    cooccurrences = {
        "pairs": {
            f"{i}-{j}": {"count": 5, "expected": 5.0, "affinity": 1.0}
            for i in range(1, 50)
            for j in range(i + 1, 50)
        },
        "expected_pair_count": 5.0,
        "matrix_shape": [49, 49],
    }
    return {
        "frequency": frequencies,
        "gaps": gaps,
        "cooccurrence": cooccurrences,
    }


@pytest.fixture
def small_statistics():
    """Minimal statistics for the small game (10 numbers)."""
    frequencies = {
        str(n): {"count": 10, "relative": 0.1, "ratio": 1.0, "last_seen": 0} for n in range(1, 11)
    }
    gaps = {
        str(n): {
            "current_gap": 3,
            "avg_gap": 5.0,
            "max_gap": 10,
            "min_gap": 1,
            "median_gap": 4.0,
            "expected_gap": 5.0,
        }
        for n in range(1, 11)
    }
    cooccurrences = {
        "pairs": {
            f"{i}-{j}": {"count": 5, "expected": 5.0, "affinity": 1.0}
            for i in range(1, 11)
            for j in range(i + 1, 11)
        },
        "expected_pair_count": 5.0,
        "matrix_shape": [10, 10],
    }
    return {
        "frequency": frequencies,
        "gaps": gaps,
        "cooccurrence": cooccurrences,
    }


# ── BaseOptimizer ──


class TestBaseOptimizer:
    def test_random_grid_valid(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(scorer, small_statistics, small_config, seed=42)
        grid = sa._random_grid()
        assert len(grid) == small_config.numbers_drawn
        assert grid == sorted(grid)
        assert all(small_config.min_number <= n <= small_config.max_number for n in grid)
        assert len(set(grid)) == len(grid)

    def test_neighbor_valid(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(scorer, small_statistics, small_config, seed=42)
        grid = [1, 3, 5]
        neighbor = sa._neighbor(grid)
        assert len(neighbor) == len(grid)
        assert neighbor == sorted(neighbor)
        assert len(set(neighbor)) == len(neighbor)
        # Exactly one difference
        assert len(set(grid) ^ set(neighbor)) == 2

    def test_score_returns_scored_result(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(scorer, small_statistics, small_config, seed=42)
        result = sa._score([1, 3, 5])
        assert isinstance(result, ScoredResult)
        assert 0 <= result.total_score <= 1


# ── SimulatedAnnealing ──


class TestSimulatedAnnealing:
    def test_optimize_returns_correct_count(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(
            scorer,
            small_statistics,
            small_config,
            max_iterations=100,
            seed=42,
        )
        results = sa.optimize(n_grids=3)
        assert len(results) == 3
        assert all(isinstance(r, ScoredResult) for r in results)

    def test_results_sorted_descending(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(
            scorer,
            small_statistics,
            small_config,
            max_iterations=100,
            seed=42,
        )
        results = sa.optimize(n_grids=5)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_grids_are_valid(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(
            scorer,
            small_statistics,
            small_config,
            max_iterations=50,
            seed=42,
        )
        results = sa.optimize(n_grids=2)
        for r in results:
            assert len(r.numbers) == small_config.numbers_drawn
            assert r.numbers == sorted(r.numbers)
            assert len(set(r.numbers)) == len(r.numbers)

    def test_seed_reproducibility(self, small_config, small_statistics):
        scorer = GridScorer()
        r1 = SimulatedAnnealing(
            scorer, small_statistics, small_config, max_iterations=50, seed=123
        ).optimize(2)
        r2 = SimulatedAnnealing(
            scorer, small_statistics, small_config, max_iterations=50, seed=123
        ).optimize(2)
        assert [r.numbers for r in r1] == [r.numbers for r in r2]

    def test_temperature_floor_stops_early(self, small_config, small_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(
            scorer,
            small_statistics,
            small_config,
            t_initial=0.001,
            t_min=0.01,  # t_initial < t_min → immediate stop
            max_iterations=10000,
            seed=42,
        )
        results = sa.optimize(n_grids=1)
        assert len(results) == 1


# ── GeneticAlgorithm ──


class TestGeneticAlgorithm:
    def test_optimize_returns_correct_count(self, small_config, small_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            population_size=20,
            max_generations=5,
            seed=42,
        )
        results = ga.optimize(n_grids=3)
        assert len(results) == 3

    def test_results_sorted(self, small_config, small_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            population_size=20,
            max_generations=5,
            seed=42,
        )
        results = ga.optimize(n_grids=5)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_crossover_produces_valid_child(self, small_config, small_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=1,
            seed=42,
        )
        child = ga._crossover([1, 3, 5], [2, 4, 6])
        assert len(child) == small_config.numbers_drawn
        assert child == sorted(child)
        assert len(set(child)) == len(child)

    def test_mutate_keeps_valid_grid(self, small_config, small_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            mutation_rate=1.0,
            seed=42,
        )
        mutated = ga._mutate([1, 3, 5])
        assert len(mutated) == small_config.numbers_drawn
        assert mutated == sorted(mutated)
        assert len(set(mutated)) == len(mutated)

    def test_tournament_selection(self, small_config, small_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            tournament_size=2,
            seed=42,
        )
        pop = [
            ScoredResult(numbers=[1, 2, 3], total_score=0.5, score_breakdown={}),
            ScoredResult(numbers=[4, 5, 6], total_score=0.9, score_breakdown={}),
            ScoredResult(numbers=[7, 8, 9], total_score=0.1, score_breakdown={}),
        ]
        winner = ga._tournament_select(pop)
        assert isinstance(winner, ScoredResult)

    def test_seed_reproducibility(self, small_config, small_statistics):
        scorer = GridScorer()
        r1 = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=3,
            seed=99,
        ).optimize(2)
        r2 = GeneticAlgorithm(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=3,
            seed=99,
        ).optimize(2)
        assert [r.numbers for r in r1] == [r.numbers for r in r2]


# ── TabuSearch ──


class TestTabuSearch:
    def test_optimize_returns_correct_count(self, small_config, small_statistics):
        scorer = GridScorer()
        ts = TabuSearch(
            scorer,
            small_statistics,
            small_config,
            max_iterations=50,
            tabu_size=10,
            n_neighbors=5,
            seed=42,
        )
        results = ts.optimize(n_grids=3)
        assert len(results) == 3

    def test_results_sorted(self, small_config, small_statistics):
        scorer = GridScorer()
        ts = TabuSearch(
            scorer,
            small_statistics,
            small_config,
            max_iterations=50,
            tabu_size=10,
            n_neighbors=5,
            seed=42,
        )
        results = ts.optimize(n_grids=4)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_valid_grids(self, small_config, small_statistics):
        scorer = GridScorer()
        ts = TabuSearch(
            scorer,
            small_statistics,
            small_config,
            max_iterations=20,
            n_neighbors=3,
            seed=42,
        )
        results = ts.optimize(n_grids=2)
        for r in results:
            assert len(r.numbers) == small_config.numbers_drawn
            assert r.numbers == sorted(r.numbers)

    def test_seed_reproducibility(self, small_config, small_statistics):
        scorer = GridScorer()
        r1 = TabuSearch(
            scorer,
            small_statistics,
            small_config,
            max_iterations=20,
            n_neighbors=3,
            seed=55,
        ).optimize(2)
        r2 = TabuSearch(
            scorer,
            small_statistics,
            small_config,
            max_iterations=20,
            n_neighbors=3,
            seed=55,
        ).optimize(2)
        assert [r.numbers for r in r1] == [r.numbers for r in r2]


# ── HillClimbing ──


class TestHillClimbing:
    def test_optimize_returns_correct_count(self, small_config, small_statistics):
        scorer = GridScorer()
        hc = HillClimbing(
            scorer,
            small_statistics,
            small_config,
            n_restarts=5,
            max_no_improve=10,
            seed=42,
        )
        results = hc.optimize(n_grids=3)
        assert len(results) == 3

    def test_results_sorted(self, small_config, small_statistics):
        scorer = GridScorer()
        hc = HillClimbing(
            scorer,
            small_statistics,
            small_config,
            n_restarts=5,
            max_no_improve=10,
            seed=42,
        )
        results = hc.optimize(n_grids=5)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_valid_grids(self, small_config, small_statistics):
        scorer = GridScorer()
        hc = HillClimbing(
            scorer,
            small_statistics,
            small_config,
            n_restarts=3,
            max_no_improve=5,
            seed=42,
        )
        results = hc.optimize(n_grids=2)
        for r in results:
            assert len(r.numbers) == small_config.numbers_drawn
            assert r.numbers == sorted(r.numbers)

    def test_seed_reproducibility(self, small_config, small_statistics):
        scorer = GridScorer()
        r1 = HillClimbing(
            scorer,
            small_statistics,
            small_config,
            n_restarts=3,
            max_no_improve=5,
            seed=77,
        ).optimize(2)
        r2 = HillClimbing(
            scorer,
            small_statistics,
            small_config,
            n_restarts=3,
            max_no_improve=5,
            seed=77,
        ).optimize(2)
        assert [r.numbers for r in r1] == [r.numbers for r in r2]


# ── MultiObjectiveOptimizer ──


class TestMultiObjectiveOptimizer:
    def test_optimize_returns_correct_count(self, small_config, small_statistics):
        scorer = GridScorer()
        mo = MultiObjectiveOptimizer(
            scorer,
            small_statistics,
            small_config,
            population_size=15,
            max_generations=3,
            seed=42,
        )
        results = mo.optimize(n_grids=3)
        assert len(results) == 3

    def test_results_sorted(self, small_config, small_statistics):
        scorer = GridScorer()
        mo = MultiObjectiveOptimizer(
            scorer,
            small_statistics,
            small_config,
            population_size=15,
            max_generations=3,
            seed=42,
        )
        results = mo.optimize(n_grids=5)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_dominates(self, small_config, small_statistics):
        scorer = GridScorer()
        mo = MultiObjectiveOptimizer(scorer, small_statistics, small_config, seed=42)
        assert mo._dominates((0.9, 0.8, 0.7), (0.8, 0.7, 0.6))
        assert not mo._dominates((0.9, 0.5, 0.7), (0.8, 0.7, 0.6))
        assert not mo._dominates((0.8, 0.7, 0.6), (0.8, 0.7, 0.6))

    def test_hamming_distance(self):
        assert MultiObjectiveOptimizer._hamming_distance([1, 2, 3], [1, 2, 3]) == 0
        assert MultiObjectiveOptimizer._hamming_distance([1, 2, 3], [4, 5, 6]) == 6
        assert MultiObjectiveOptimizer._hamming_distance([1, 2, 3], [1, 4, 5]) == 4

    def test_valid_grids(self, small_config, small_statistics):
        scorer = GridScorer()
        mo = MultiObjectiveOptimizer(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=2,
            seed=42,
        )
        results = mo.optimize(n_grids=2)
        for r in results:
            assert len(r.numbers) == small_config.numbers_drawn
            assert r.numbers == sorted(r.numbers)

    def test_seed_reproducibility(self, small_config, small_statistics):
        scorer = GridScorer()
        r1 = MultiObjectiveOptimizer(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=2,
            seed=42,
        ).optimize(3)
        r2 = MultiObjectiveOptimizer(
            scorer,
            small_statistics,
            small_config,
            population_size=10,
            max_generations=2,
            seed=42,
        ).optimize(3)
        assert [r.numbers for r in r1] == [r.numbers for r in r2]


# ── PortfolioOptimizer ──


class TestPortfolioOptimizer:
    @pytest.fixture
    def candidates(self):
        """Generate a set of candidate ScoredResults."""
        return [
            ScoredResult(numbers=[1, 2, 3], total_score=0.90, score_breakdown={}),
            ScoredResult(numbers=[4, 5, 6], total_score=0.85, score_breakdown={}),
            ScoredResult(numbers=[7, 8, 9], total_score=0.80, score_breakdown={}),
            ScoredResult(numbers=[1, 4, 7], total_score=0.75, score_breakdown={}),
            ScoredResult(numbers=[2, 5, 8], total_score=0.70, score_breakdown={}),
            ScoredResult(numbers=[3, 6, 9], total_score=0.65, score_breakdown={}),
            ScoredResult(numbers=[1, 5, 9], total_score=0.88, score_breakdown={}),
            ScoredResult(numbers=[2, 6, 10], total_score=0.72, score_breakdown={}),
        ]

    def test_optimize_balanced(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=3, strategy="balanced")
        assert isinstance(result, PortfolioResult)
        assert len(result.grids) == 3
        assert result.strategy == "balanced"

    def test_optimize_max_diversity(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=3, strategy="max_diversity")
        assert result.diversity_score >= 0

    def test_optimize_max_coverage(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=4, strategy="max_coverage")
        assert result.coverage_score >= 0

    def test_optimize_min_correlation(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=3, strategy="min_correlation")
        assert result.min_hamming_distance >= 0

    def test_unknown_strategy_raises(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        with pytest.raises(ValueError, match="Unknown strategy"):
            po.optimize(candidates, target_size=3, strategy="nonexistent")

    def test_empty_candidates(self, small_config):
        po = PortfolioOptimizer(small_config)
        result = po.optimize([], target_size=3, strategy="balanced")
        assert len(result.grids) == 0
        assert result.diversity_score == 0.0

    def test_hamming_distance(self):
        assert PortfolioOptimizer._hamming_distance([1, 2, 3], [1, 2, 3]) == 0
        assert PortfolioOptimizer._hamming_distance([1, 2, 3], [4, 5, 6]) == 6

    def test_avg_score_positive(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=3, strategy="balanced")
        assert result.avg_grid_score > 0

    def test_grids_are_from_candidates(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=3, strategy="balanced")
        candidate_numbers = [c.numbers for c in candidates]
        for g in result.grids:
            assert g.numbers in candidate_numbers

    def test_target_size_capped_at_candidates(self, small_config, candidates):
        po = PortfolioOptimizer(small_config)
        result = po.optimize(candidates, target_size=100, strategy="balanced")
        assert len(result.grids) == len(candidates)


# ── Method selector ──


class TestMethodSelector:
    def test_small_batch_returns_hill_climbing(self):
        game = GameConfig(
            name="Tiny",
            slug="tiny",
            numbers_pool=10,
            numbers_drawn=3,
            min_number=1,
            max_number=10,
        )
        method = select_method(game, n_grids=3)
        assert method == "hill_climbing"

    def test_medium_batch_moderate_space_returns_tabu(self):
        game = GameConfig(
            name="Loto",
            slug="loto",
            numbers_pool=49,
            numbers_drawn=5,
            min_number=1,
            max_number=49,
        )
        # comb(49, 5) ≈ 1.9M < 10M → tabu
        method = select_method(game, n_grids=5)
        assert method == "tabu"

    def test_medium_batch_large_space_returns_annealing(self):
        game = GameConfig(
            name="Mega",
            slug="mega",
            numbers_pool=70,
            numbers_drawn=5,
            min_number=1,
            max_number=70,
        )
        # comb(70, 5) ≈ 12.1M > 10M → annealing
        method = select_method(game, n_grids=7)
        assert method == "annealing"

    def test_large_batch_returns_genetic(self):
        game = GameConfig(
            name="Loto",
            slug="loto",
            numbers_pool=49,
            numbers_drawn=5,
            min_number=1,
            max_number=49,
        )
        method = select_method(game, n_grids=25)
        assert method == "genetic"

    def test_boundary_ten_grids_returns_genetic(self):
        game = GameConfig(
            name="Loto",
            slug="loto",
            numbers_pool=49,
            numbers_drawn=5,
            min_number=1,
            max_number=49,
        )
        method = select_method(game, n_grids=10)
        assert method == "genetic"


# ── Strategy weights ──


class TestStrategyWeights:
    def test_all_strategies_defined(self):
        assert set(STRATEGY_WEIGHTS.keys()) == {
            "balanced",
            "max_diversity",
            "max_coverage",
            "min_correlation",
        }

    def test_weights_sum_to_one(self):
        for name, weights in STRATEGY_WEIGHTS.items():
            assert abs(sum(weights) - 1.0) < 1e-9, f"Strategy '{name}' weights don't sum to 1"

    def test_all_positive(self):
        for name, weights in STRATEGY_WEIGHTS.items():
            assert all(w > 0 for w in weights), f"Strategy '{name}' has non-positive weight"
