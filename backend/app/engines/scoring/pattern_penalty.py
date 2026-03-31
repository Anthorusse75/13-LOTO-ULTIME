"""Pattern penalty criterion."""

from typing import Any

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class PatternPenalty(BaseScoringCriterion):
    """Detect and penalise overly regular patterns (arithmetic sequences, etc.)."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs: Any) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        penalties: list[float] = []

        diffs = [sorted_grid[i + 1] - sorted_grid[i] for i in range(k - 1)]

        # Perfect arithmetic sequence
        if len(set(diffs)) == 1 and k > 2:
            penalties.append(1.0)

        # Consecutive numbers (diff == 1)
        consecutive_count = sum(1 for d in diffs if d == 1)
        if consecutive_count >= 3:
            penalties.append(0.5)
        elif consecutive_count >= 2:
            penalties.append(0.2)

        # All multiples of the same number
        for m in range(2, 10):
            if all(n % m == 0 for n in grid):
                penalties.append(0.8)
                break

        # All in the same decade
        decades = {(n - 1) // 10 for n in grid}
        if len(decades) == 1 and k > 1:
            penalties.append(0.6)

        # All even or all odd
        parities = {n % 2 for n in grid}
        if len(parities) == 1 and k > 1:
            penalties.append(0.4)

        # Span too narrow
        span = sorted_grid[-1] - sorted_grid[0]
        if span < 15 and k > 1:
            penalties.append(0.3 * (1 - span / 15))

        return min(sum(penalties), 0.7)

    def get_name(self) -> str:
        return "pattern_penalty"
