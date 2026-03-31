"""Temporal trend analysis engine."""

from typing import Any

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine

DEFAULT_WINDOWS = [20, 50, 100, 200]
MIN_R2_THRESHOLD = 0.5


class TemporalEngine(BaseStatisticsEngine):
    """Analyze frequency trends over sliding windows."""

    def __init__(self, windows: list[int] | None = None):
        self.WINDOWS = windows or DEFAULT_WINDOWS

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict[int | str, Any]:
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

    def _compute_momentum(self, draws: np.ndarray, game: GameConfig) -> dict[int | str, Any]:
        """Compute momentum via linear regression on sliding window frequencies.

        Only returns trends with R² > MIN_R2_THRESHOLD.
        """
        n_draws = draws.shape[0]
        available_windows = [w for w in self.WINDOWS if n_draws >= w]
        if len(available_windows) < 2:
            return {}

        momentum: dict[int | str, Any] = {}
        x = np.arange(len(available_windows), dtype=float)
        x_mean = x.mean()
        ss_xx = float(((x - x_mean) ** 2).sum())

        for num in range(game.min_number, game.max_number + 1):
            freqs = []
            for w in available_windows:
                recent = draws[-w:]
                mask = np.any(recent == num, axis=1)
                freqs.append(float(mask.sum() / w))

            y = np.array(freqs)
            y_mean = y.mean()

            if len(x) < 2 or ss_xx == 0:
                continue

            # Linear regression coefficients
            ss_xy = float(((x - x_mean) * (y - y_mean)).sum())
            slope = ss_xy / ss_xx

            # R² computation
            ss_yy = float(((y - y_mean) ** 2).sum())
            r_squared = (ss_xy**2) / (ss_xx * ss_yy) if ss_yy > 0 else 0.0

            if r_squared >= MIN_R2_THRESHOLD:
                momentum[num] = {
                    "slope": round(slope, 6),
                    "r_squared": round(r_squared, 4),
                }

        return momentum

    def get_name(self) -> str:
        return "temporal"
