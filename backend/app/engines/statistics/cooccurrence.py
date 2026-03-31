"""Cooccurrence analysis engine."""

from typing import Any

import numpy as np

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine


class CooccurrenceEngine(BaseStatisticsEngine):
    """Compute cooccurrence matrix and pair affinities."""

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict[int | str, Any]:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {"pairs": {}, "expected_pair_count": 0, "matrix_shape": [0, 0]}

        n = game.numbers_pool
        k = game.numbers_drawn
        min_num = game.min_number

        # Binary presence matrix (N draws × n numbers)
        binary_matrix = np.zeros((n_draws, n), dtype=np.int8)
        for t in range(n_draws):
            for num in draws[t]:
                binary_matrix[t, num - min_num] = 1

        # Cooccurrence matrix = M^T × M
        cooc_matrix = binary_matrix.T @ binary_matrix

        # Expected pair cooccurrence under independence
        expected_pair = n_draws * k * (k - 1) / (n * (n - 1)) if n > 1 else 0

        # Extract significant pairs
        pairs = {}
        for i in range(n):
            for j in range(i + 1, n):
                num_i = i + min_num
                num_j = j + min_num
                count = int(cooc_matrix[i, j])
                affinity = round(count / expected_pair, 4) if expected_pair > 0 else 0
                pairs[f"{num_i}-{num_j}"] = {
                    "count": count,
                    "expected": round(expected_pair, 2),
                    "affinity": affinity,
                }

        return {
            "pairs": pairs,
            "expected_pair_count": round(expected_pair, 2),
            "matrix_shape": [n, n],
        }

    def get_cooccurrence_matrix(self, draws: np.ndarray, game: GameConfig) -> np.ndarray:
        """Return the raw cooccurrence matrix (used by GraphEngine)."""
        n_draws = draws.shape[0]
        if n_draws == 0:
            return np.zeros((game.numbers_pool, game.numbers_pool), dtype=np.int32)

        n = game.numbers_pool
        min_num = game.min_number

        binary_matrix = np.zeros((n_draws, n), dtype=np.int8)
        for t in range(n_draws):
            for num in draws[t]:
                binary_matrix[t, num - min_num] = 1

        return (binary_matrix.T @ binary_matrix).astype(np.int32)

    def get_name(self) -> str:
        return "cooccurrence"
