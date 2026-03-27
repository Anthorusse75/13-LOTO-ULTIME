"""Bayesian (Beta-Binomial) analysis engine."""

import numpy as np
from scipy.stats import beta as beta_dist

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class BayesianEngine(BaseStatisticsEngine):
    """Bayesian estimation using Beta-Binomial model with Jeffreys prior."""

    ALPHA_PRIOR = 0.5  # Jeffreys prior
    BETA_PRIOR = 0.5

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {}

        results = {}

        for num in range(game.min_number, game.max_number + 1):
            count = int(np.any(draws == num, axis=1).sum())

            alpha = self.ALPHA_PRIOR + count
            beta = self.BETA_PRIOR + (n_draws - count)

            posterior_mean = alpha / (alpha + beta)
            ci_low, ci_high = beta_dist.ppf([0.025, 0.975], alpha, beta)

            results[num] = {
                "alpha": round(alpha, 2),
                "beta": round(beta, 2),
                "posterior_mean": round(posterior_mean, 6),
                "ci_95_low": round(float(ci_low), 6),
                "ci_95_high": round(float(ci_high), 6),
                "ci_width": round(float(ci_high - ci_low), 6),
            }

        return results

    def get_name(self) -> str:
        return "bayesian"
