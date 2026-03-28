"""Balance scoring criterion."""

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class BalanceCriterion(BaseScoringCriterion):
    """Score based on spatial distribution — measures spread uniformity."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        n = game.max_number - game.min_number + 1

        # Ideal positions (uniform spread)
        ideal_positions = [
            game.min_number + (i + 1) * n / (k + 1) for i in range(k)
        ]

        # Average normalised deviation
        deviations = [abs(sorted_grid[i] - ideal_positions[i]) / n for i in range(k)]

        avg_deviation = sum(deviations) / k
        score = 1 - min(avg_deviation * 2, 1)

        return max(0.0, min(1.0, score))

    def get_name(self) -> str:
        return "balance"
