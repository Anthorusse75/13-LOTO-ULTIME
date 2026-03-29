"""Unit tests for temporal engine R² and configurable windows."""

import numpy as np

from app.core.game_definitions import GameConfig
from app.engines.statistics.temporal import DEFAULT_WINDOWS, MIN_R2_THRESHOLD, TemporalEngine


def _make_game():
    return GameConfig(
        name="Test Loto",
        slug="test-loto",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        draw_frequency="3/week",
        historical_source="test",
    )


def _make_draws(n: int, game: GameConfig, rng=None) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng(42)
    draws = []
    for _ in range(n):
        nums = sorted(
            rng.choice(
                range(game.min_number, game.max_number + 1), game.numbers_drawn, replace=False
            )
        )
        draws.append(nums)
    return np.array(draws)


class TestTemporalEngineConfig:
    def test_default_windows(self):
        engine = TemporalEngine()
        assert engine.WINDOWS == DEFAULT_WINDOWS

    def test_custom_windows(self):
        engine = TemporalEngine(windows=[10, 30, 60])
        assert engine.WINDOWS == [10, 30, 60]

    def test_get_name(self):
        engine = TemporalEngine()
        assert engine.get_name() == "temporal"


class TestTemporalEngineCompute:
    def test_empty_draws(self):
        engine = TemporalEngine()
        game = _make_game()
        result = engine.compute(np.array([]).reshape(0, 5), game)
        assert result == {"windows": []}

    def test_compute_with_data(self):
        engine = TemporalEngine(windows=[10, 20, 50])
        game = _make_game()
        draws = _make_draws(60, game)
        result = engine.compute(draws, game)
        assert "windows" in result
        assert "momentum" in result
        # Should have windows that fit (10, 20, 50 all <= 60)
        assert len(result["windows"]) == 3

    def test_compute_skips_large_windows(self):
        engine = TemporalEngine(windows=[10, 20, 500])
        game = _make_game()
        draws = _make_draws(30, game)
        result = engine.compute(draws, game)
        # Only 10 and 20 fit
        assert len(result["windows"]) == 2


class TestMomentumR2:
    def test_momentum_has_r_squared(self):
        engine = TemporalEngine(windows=[10, 20, 50])
        game = _make_game()
        draws = _make_draws(60, game)
        result = engine.compute(draws, game)
        for _num, data in result["momentum"].items():
            assert "slope" in data
            assert "r_squared" in data
            assert data["r_squared"] >= MIN_R2_THRESHOLD

    def test_momentum_filters_low_r2(self):
        engine = TemporalEngine(windows=[10, 20, 50])
        game = _make_game()
        draws = _make_draws(60, game)
        result = engine.compute(draws, game)
        # All returned momentum entries should have R² >= threshold
        for _num, data in result["momentum"].items():
            assert data["r_squared"] >= MIN_R2_THRESHOLD

    def test_momentum_empty_with_few_windows(self):
        engine = TemporalEngine(windows=[10])
        game = _make_game()
        draws = _make_draws(15, game)
        result = engine.compute(draws, game)
        # Only 1 available window -> no momentum
        assert result["momentum"] == {}
