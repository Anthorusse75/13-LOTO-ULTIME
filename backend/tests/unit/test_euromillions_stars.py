"""Tests for EuroMillions star support across the full pipeline."""

import numpy as np
import pytest

from app.core.game_definitions import GameConfig
from app.engines.optimization.genetic import GeneticAlgorithm
from app.engines.optimization.hill_climbing import HillClimbing
from app.engines.optimization.simulated_annealing import SimulatedAnnealing
from app.engines.optimization.tabu import TabuSearch
from app.engines.scoring.scorer import GridScorer
from app.engines.statistics.frequency import FrequencyEngine
from app.engines.statistics.gap import GapEngine


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
def loto_config():
    return GameConfig(
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
def star_draws():
    """Simulated star draws: 50 draws of 2 stars each (EuroMillions-like)."""
    rng = np.random.default_rng(42)
    return np.array([sorted(rng.choice(range(1, 13), size=2, replace=False)) for _ in range(50)])


@pytest.fixture
def star_game():
    """Virtual GameConfig for star statistics computation."""
    return GameConfig(
        name="Stars",
        slug="stars",
        numbers_pool=12,
        numbers_drawn=2,
        min_number=1,
        max_number=12,
    )


@pytest.fixture
def euromillions_statistics(star_draws, star_game):
    """Build a statistics dict with star data included."""
    # Main number stats (simplified)
    freq = {str(n): {"count": 10, "relative": 0.2, "ratio": 1.0, "last_seen": 0} for n in range(1, 51)}
    gaps = {
        str(n): {"current_gap": 3, "avg_gap": 5.0, "max_gap": 10, "min_gap": 1, "median_gap": 4.0, "expected_gap": 10.0}
        for n in range(1, 51)
    }
    cooc = {"pairs": {}, "expected_pair_count": 5.0, "matrix_shape": [50, 50]}

    # Star stats computed from actual engine
    star_freq = FrequencyEngine().compute(star_draws, star_game)
    star_gaps = GapEngine().compute(star_draws, star_game)

    return {
        "frequency": freq,
        "gaps": gaps,
        "cooccurrence": cooc,
        "star_frequency": star_freq,
        "star_gaps": star_gaps,
    }


# ── Star statistics computation ──


class TestStarStatisticsEngines:
    def test_frequency_engine_on_stars(self, star_draws, star_game):
        result = FrequencyEngine().compute(star_draws, star_game)
        assert len(result) == 12
        for num in range(1, 13):
            assert num in result
            assert "count" in result[num]
            assert "ratio" in result[num]
            assert result[num]["count"] >= 0

    def test_gap_engine_on_stars(self, star_draws, star_game):
        result = GapEngine().compute(star_draws, star_game)
        assert len(result) == 12
        for num in range(1, 13):
            assert num in result
            assert "current_gap" in result[num]
            assert "avg_gap" in result[num]

    def test_star_stats_differ_from_number_stats(self, star_draws, star_game):
        """Star and number stats produce different results for different data."""
        number_draws = np.array([sorted(np.random.default_rng(42).choice(range(1, 51), size=5, replace=False)) for _ in range(50)])
        number_game = GameConfig(
            name="Numbers", slug="numbers", numbers_pool=50, numbers_drawn=5, min_number=1, max_number=50
        )
        star_freq = FrequencyEngine().compute(star_draws, star_game)
        number_freq = FrequencyEngine().compute(number_draws, number_game)
        # Different pool sizes → different number of keys
        assert len(star_freq) != len(number_freq)


# ── Optimizer star generation ──


class TestOptimizerStarSupport:
    def test_random_stars_euromillions(self, euromillions_config):
        scorer = GridScorer()
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        opt = SimulatedAnnealing(scorer, stats, euromillions_config, seed=42)
        stars = opt._random_stars()
        assert len(stars) == 2
        assert all(1 <= s <= 12 for s in stars)
        assert stars == sorted(stars)
        assert len(set(stars)) == 2

    def test_random_stars_loto(self, loto_config):
        scorer = GridScorer()
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        opt = SimulatedAnnealing(scorer, stats, loto_config, seed=42)
        stars = opt._random_stars()
        assert len(stars) == 1
        assert 1 <= stars[0] <= 10

    def test_random_stars_no_stars_game(self):
        """A game without stars returns empty list."""
        game = GameConfig(name="NoStars", slug="ns", numbers_pool=10, numbers_drawn=3, min_number=1, max_number=10)
        scorer = GridScorer()
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        opt = SimulatedAnnealing(scorer, stats, game, seed=42)
        assert opt._random_stars() == []

    def test_star_neighbor(self, euromillions_config):
        scorer = GridScorer()
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        opt = SimulatedAnnealing(scorer, stats, euromillions_config, seed=42)
        stars = [3, 7]
        neighbor = opt._star_neighbor(stars)
        assert len(neighbor) == 2
        assert all(1 <= s <= 12 for s in neighbor)
        assert neighbor == sorted(neighbor)
        # Exactly one star changed
        assert len(set(stars) ^ set(neighbor)) == 2

    def test_star_neighbor_empty(self, euromillions_config):
        scorer = GridScorer()
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        opt = SimulatedAnnealing(scorer, stats, euromillions_config, seed=42)
        assert opt._star_neighbor([]) == []


# ── Optimizers produce stars in results ──


class TestOptimizersProduceStars:
    def test_genetic_produces_stars(self, euromillions_config, euromillions_statistics):
        scorer = GridScorer()
        ga = GeneticAlgorithm(
            scorer, euromillions_statistics, euromillions_config,
            population_size=20, max_generations=5, seed=42,
        )
        results = ga.optimize(n_grids=3)
        assert len(results) == 3
        for r in results:
            assert r.stars is not None
            assert len(r.stars) == 2
            assert all(1 <= s <= 12 for s in r.stars)
            assert r.star_score is not None

    def test_sa_produces_stars(self, euromillions_config, euromillions_statistics):
        scorer = GridScorer()
        sa = SimulatedAnnealing(
            scorer, euromillions_statistics, euromillions_config,
            max_iterations=100, seed=42,
        )
        results = sa.optimize(n_grids=2)
        assert len(results) == 2
        for r in results:
            assert r.stars is not None
            assert len(r.stars) == 2

    def test_tabu_produces_stars(self, euromillions_config, euromillions_statistics):
        scorer = GridScorer()
        tabu = TabuSearch(
            scorer, euromillions_statistics, euromillions_config,
            max_iterations=50, n_neighbors=5, seed=42,
        )
        results = tabu.optimize(n_grids=2)
        assert len(results) == 2
        for r in results:
            assert r.stars is not None
            assert len(r.stars) == 2

    def test_hc_produces_stars(self, euromillions_config, euromillions_statistics):
        scorer = GridScorer()
        hc = HillClimbing(
            scorer, euromillions_statistics, euromillions_config,
            n_restarts=5, max_no_improve=10, seed=42,
        )
        results = hc.optimize(n_grids=2)
        assert len(results) == 2
        for r in results:
            assert r.stars is not None
            assert len(r.stars) == 2

    def test_no_stars_game_still_works(self):
        """Optimizers still work for games without stars."""
        game = GameConfig(name="Mini", slug="mini", numbers_pool=10, numbers_drawn=3, min_number=1, max_number=10)
        freq = {n: {"count": 10, "relative": 0.3, "ratio": 1.0, "last_seen": 0} for n in range(1, 11)}
        gaps = {n: {"current_gap": 3, "avg_gap": 5.0, "max_gap": 10, "min_gap": 1, "median_gap": 4.0, "expected_gap": 3.3} for n in range(1, 11)}
        stats = {"frequency": freq, "gaps": gaps, "cooccurrence": {"pairs": {}, "expected_pair_count": 5.0, "matrix_shape": [10, 10]}}
        scorer = GridScorer()
        sa = SimulatedAnnealing(scorer, stats, game, max_iterations=50, seed=42)
        results = sa.optimize(n_grids=2)
        for r in results:
            assert r.stars is None
            assert r.star_score is None


# ── Scorer with stars ──


class TestScorerStarIntegration:
    def test_score_with_stars_uses_star_data(self, euromillions_statistics, euromillions_config):
        scorer = GridScorer()
        result = scorer.score_with_stars(
            [1, 10, 20, 30, 40], [3, 7], euromillions_statistics, euromillions_config
        )
        assert result.stars == [3, 7]
        assert result.star_score is not None
        assert 0.0 <= result.star_score <= 1.0
        assert 0.0 <= result.total_score <= 1.0

    def test_score_without_star_data_returns_neutral(self, euromillions_config):
        """When no star_frequency/star_gaps in stats, fallback to 0.5."""
        stats = {"frequency": {}, "gaps": {}, "cooccurrence": {}}
        scorer = GridScorer()
        result = scorer.score_with_stars(
            [1, 10, 20, 30, 40], [3, 7], stats, euromillions_config
        )
        assert result.star_score == 0.5
