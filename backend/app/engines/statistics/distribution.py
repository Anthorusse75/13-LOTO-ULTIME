"""Distribution analysis engine."""

import numpy as np
from scipy import stats as sp_stats

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class DistributionEngine(BaseStatisticsEngine):
    """Compute distribution statistics: entropy, chi-2, sums, even/odd."""

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {}

        n = game.numbers_pool
        k = game.numbers_drawn
        min_num = game.min_number

        # Frequency counts per number
        counts = np.zeros(n, dtype=int)
        for num in range(min_num, game.max_number + 1):
            idx = num - min_num
            counts[idx] = int(np.any(draws == num, axis=1).sum())

        # Shannon entropy
        total = counts.sum()
        probs = counts / total if total > 0 else np.zeros(n)
        nonzero = probs[probs > 0]
        entropy = float(-np.sum(nonzero * np.log2(nonzero)))
        max_entropy = float(np.log2(n)) if n > 0 else 0.0
        uniformity = entropy / max_entropy if max_entropy > 0 else 0

        # Chi-2 goodness of fit
        expected = np.full(n, n_draws * k / n)
        chi2_stat, chi2_pvalue = sp_stats.chisquare(counts, f_exp=expected)

        # Sum of numbers per draw
        sums = draws.sum(axis=1)

        # Even/odd ratio
        even_counts = np.sum(draws % 2 == 0, axis=1)

        # Decade distribution
        decade_size = 10
        n_decades = (n + decade_size - 1) // decade_size
        decade_counts = np.zeros(n_decades, dtype=int)
        for d_idx in range(n_decades):
            low = min_num + d_idx * decade_size
            high = min(min_num + (d_idx + 1) * decade_size - 1, game.max_number)
            for num in range(low, high + 1):
                decade_counts[d_idx] += int(np.any(draws == num, axis=1).sum())

        decades = {}
        for d_idx in range(n_decades):
            low = min_num + d_idx * decade_size
            high = min(min_num + (d_idx + 1) * decade_size - 1, game.max_number)
            decades[f"{low}-{high}"] = int(decade_counts[d_idx])

        return {
            "entropy": round(entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "uniformity_score": round(uniformity, 4),
            "chi2_statistic": round(float(chi2_stat), 4),
            "chi2_pvalue": round(float(chi2_pvalue), 6),
            "is_uniform": bool(chi2_pvalue > 0.05),
            "sum_stats": {
                "mean": round(float(sums.mean()), 2),
                "std": round(float(sums.std()), 2),
                "min": int(sums.min()),
                "max": int(sums.max()),
                "median": float(np.median(sums)),
            },
            "even_odd_distribution": {
                "mean_even": round(float(even_counts.mean()), 2),
                "mean_odd": round(float(k - even_counts.mean()), 2),
            },
            "decades": decades,
        }

    def get_name(self) -> str:
        return "distribution"
