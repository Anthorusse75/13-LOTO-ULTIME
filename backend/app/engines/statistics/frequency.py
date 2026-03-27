"""Frequency analysis engine."""

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class FrequencyEngine(BaseStatisticsEngine):
    """Compute frequency statistics for each number."""

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {}

        theoretical_p = game.numbers_drawn / game.numbers_pool
        frequencies = {}

        for num in range(game.min_number, game.max_number + 1):
            mask = np.any(draws == num, axis=1)
            count = int(mask.sum())
            relative = count / n_draws

            # Last seen: number of draws since last appearance
            appearances = np.where(mask)[0]
            last_seen = (n_draws - 1 - appearances[-1]) if len(appearances) > 0 else n_draws

            frequencies[num] = {
                "count": count,
                "relative": round(relative, 6),
                "ratio": round(relative / theoretical_p, 4) if theoretical_p > 0 else 0,
                "last_seen": int(last_seen),
            }

        return frequencies

    def get_name(self) -> str:
        return "frequency"
