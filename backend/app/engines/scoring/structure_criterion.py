"""Structure scoring criterion."""

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class StructureCriterion(BaseScoringCriterion):
    """Score based on structural quality (even/odd, decades, low/high, gaps)."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        midpoint = (game.min_number + game.max_number) / 2

        # Even/odd ratio — ideal is k/2
        even_count = sum(1 for n in grid if n % 2 == 0)
        ideal_even = k / 2
        even_odd_score = 1 - abs(even_count - ideal_even) / (k / 2) if k > 0 else 0.5

        # Decade distribution
        decade_size = 10
        n_decades = (game.max_number - game.min_number) // decade_size + 1
        decade_counts = [0] * n_decades
        for n in grid:
            decade_idx = (n - game.min_number) // decade_size
            decade_counts[decade_idx] += 1
        ideal_per_decade = k / n_decades
        decade_deviation = sum(abs(c - ideal_per_decade) for c in decade_counts)
        max_deviation = k
        decade_score = 1 - decade_deviation / max_deviation if max_deviation > 0 else 0.5

        # Low/high ratio
        low_count = sum(1 for n in grid if n <= midpoint)
        low_high_score = 1 - abs(low_count - k / 2) / (k / 2) if k > 0 else 0.5

        # Consecutive gaps variety
        if k > 1:
            diffs = [sorted_grid[i + 1] - sorted_grid[i] for i in range(k - 1)]
            gap_std = float(np.std(diffs)) if len(diffs) > 1 else 0.0
            max_possible_std = (game.max_number - game.min_number) / 2
            gap_score = 1 - min(gap_std / max_possible_std, 1) if max_possible_std > 0 else 0.5
        else:
            gap_score = 0.5

        return (
            0.30 * max(0, even_odd_score)
            + 0.30 * max(0, decade_score)
            + 0.20 * max(0, low_high_score)
            + 0.20 * max(0, gap_score)
        )

    def get_name(self) -> str:
        return "structure"
