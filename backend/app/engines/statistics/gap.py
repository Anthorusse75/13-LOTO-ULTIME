"""Gap (retard) analysis engine."""

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class GapEngine(BaseStatisticsEngine):
    """Compute gap statistics for each number."""

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {}

        expected_gap = round(game.numbers_pool / game.numbers_drawn, 2)
        gaps = {}

        for num in range(game.min_number, game.max_number + 1):
            mask = np.any(draws == num, axis=1)
            positions = np.where(mask)[0]

            if len(positions) == 0:
                gaps[num] = {
                    "current_gap": n_draws,
                    "max_gap": n_draws,
                    "avg_gap": float(n_draws),
                    "min_gap": n_draws,
                    "median_gap": float(n_draws),
                    "expected_gap": expected_gap,
                }
                continue

            # Intervals between appearances
            intervals = np.diff(positions)
            current_gap = n_draws - 1 - positions[-1]

            # Include initial gap (before first appearance) and current gap
            all_gaps = np.concatenate([[positions[0]], intervals, [current_gap]])

            gaps[num] = {
                "current_gap": int(current_gap),
                "max_gap": int(all_gaps.max()),
                "avg_gap": round(float(all_gaps.mean()), 2),
                "min_gap": int(all_gaps.min()),
                "median_gap": round(float(np.median(all_gaps)), 2),
                "expected_gap": expected_gap,
            }

        return gaps

    def get_name(self) -> str:
        return "gaps"
