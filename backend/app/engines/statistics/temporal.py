"""Temporal trend analysis engine."""

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class TemporalEngine(BaseStatisticsEngine):
    """Analyze frequency trends over sliding windows."""

    WINDOWS = [20, 50, 100, 200]

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {"windows": []}

        theoretical_p = game.numbers_drawn / game.numbers_pool

        windows_data = []
        for w in self.WINDOWS:
            if n_draws < w:
                continue

            recent_draws = draws[-w:]
            hot = []
            cold = []

            for num in range(game.min_number, game.max_number + 1):
                mask = np.any(recent_draws == num, axis=1)
                freq = float(mask.sum() / w)
                delta = freq - theoretical_p

                entry = {
                    "number": num,
                    "freq": round(freq, 4),
                    "delta": round(delta, 4),
                }

                if delta > 0.02:
                    hot.append(entry)
                elif delta < -0.02:
                    cold.append(entry)

            hot.sort(key=lambda x: -x["delta"])
            cold.sort(key=lambda x: x["delta"])

            windows_data.append(
                {
                    "window_size": w,
                    "hot_numbers": hot[:10],
                    "cold_numbers": cold[:10],
                }
            )

        # Momentum: regression over window frequencies for each number
        momentum = self._compute_momentum(draws, game)

        return {"windows": windows_data, "momentum": momentum}

    def _compute_momentum(self, draws: np.ndarray, game: GameConfig) -> dict:
        """Compute momentum via linear regression on sliding window frequencies."""
        n_draws = draws.shape[0]
        available_windows = [w for w in self.WINDOWS if n_draws >= w]
        if len(available_windows) < 2:
            return {}

        momentum = {}
        x = np.arange(len(available_windows), dtype=float)

        for num in range(game.min_number, game.max_number + 1):
            freqs = []
            for w in available_windows:
                recent = draws[-w:]
                mask = np.any(recent == num, axis=1)
                freqs.append(float(mask.sum() / w))

            y = np.array(freqs)
            # Linear regression: slope
            if len(x) >= 2:
                slope = float(np.polyfit(x, y, 1)[0])
                momentum[num] = round(slope, 6)

        return momentum

    def get_name(self) -> str:
        return "temporal"
