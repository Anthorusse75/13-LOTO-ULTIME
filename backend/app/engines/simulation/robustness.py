"""Robustness analysis — bootstrap stability and random comparison."""

from dataclasses import dataclass

import numpy as np

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer
from app.engines.statistics import CooccurrenceEngine, FrequencyEngine, GapEngine


@dataclass
class StabilityResult:
    """Result of bootstrap stability analysis."""

    mean_score: float
    std_score: float
    cv: float  # Coefficient of variation
    stability: float  # 1 - CV, clamped to [0, 1]
    ci_95: tuple[float, float]
    min_score: float
    max_score: float


@dataclass
class ComparisonResult:
    """Comparison of an optimized grid vs random grids."""

    grid_score: float
    random_mean: float
    random_std: float
    percentile: float  # Position in the random distribution (0-100)
    z_score: float  # Normalized deviation


class RobustnessAnalyzer:
    """Analyze the robustness of a grid via bootstrap and random comparison."""

    def __init__(self, seed: int | None = None):
        self.rng = np.random.default_rng(seed)
        self._freq_engine = FrequencyEngine()
        self._gap_engine = GapEngine()
        self._cooc_engine = CooccurrenceEngine()

    def _compute_stats(self, draws: np.ndarray, game: GameConfig) -> dict:
        """Compute the 3 statistics needed for scoring from a draw matrix."""
        return {
            "frequency": self._freq_engine.compute(draws, game),
            "gaps": self._gap_engine.compute(draws, game),
            "cooccurrence": self._cooc_engine.compute(draws, game),
        }

    def analyze_stability(
        self,
        grid: list[int],
        draws: np.ndarray,
        game: GameConfig,
        scorer: GridScorer,
        n_bootstrap: int = 100,
    ) -> StabilityResult:
        """Bootstrap stability: resample draws, recompute stats, rescore."""
        scores = []

        for _ in range(n_bootstrap):
            indices = self.rng.choice(len(draws), size=len(draws), replace=True)
            bootstrap_draws = draws[indices]
            stats = self._compute_stats(bootstrap_draws, game)
            result = scorer.score(grid, stats, game)
            scores.append(result.total_score)

        scores_arr = np.array(scores)
        mean = float(scores_arr.mean())
        std = float(scores_arr.std())
        cv = float(std / mean) if mean > 0 else float("inf")

        return StabilityResult(
            mean_score=round(mean, 6),
            std_score=round(std, 6),
            cv=round(cv, 6),
            stability=round(max(0.0, 1.0 - min(cv, 1.0)), 6),
            ci_95=(
                round(float(np.percentile(scores_arr, 2.5)), 6),
                round(float(np.percentile(scores_arr, 97.5)), 6),
            ),
            min_score=round(float(scores_arr.min()), 6),
            max_score=round(float(scores_arr.max()), 6),
        )

    def compare_with_random(
        self,
        grid_score: float,
        game: GameConfig,
        statistics: dict,
        scorer: GridScorer,
        n_random: int = 1000,
    ) -> ComparisonResult:
        """Compare a scored grid against n_random random grids."""
        numbers = np.arange(game.min_number, game.max_number + 1)
        random_scores = []

        for _ in range(n_random):
            random_grid = sorted(
                self.rng.choice(numbers, size=game.numbers_drawn, replace=False).tolist()
            )
            result = scorer.score(random_grid, statistics, game)
            random_scores.append(result.total_score)

        random_arr = np.array(random_scores)
        random_mean = float(random_arr.mean())
        random_std = float(random_arr.std())
        percentile = float((random_arr < grid_score).mean() * 100)
        z_score = float((grid_score - random_mean) / random_std) if random_std > 0 else 0.0

        return ComparisonResult(
            grid_score=round(grid_score, 6),
            random_mean=round(random_mean, 6),
            random_std=round(random_std, 6),
            percentile=round(percentile, 2),
            z_score=round(z_score, 4),
        )
