"""Simulated Annealing optimizer."""

import numpy as np

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult

from .base import BaseOptimizer


class SimulatedAnnealing(BaseOptimizer):
    """Explore grid space using simulated annealing with exponential cooling."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        t_initial: float = 1.0,
        t_min: float = 0.001,
        cooling_rate: float = 0.9995,
        max_iterations: int = 50000,
        seed: int | None = None,
    ):
        super().__init__(scorer, statistics, game, seed)
        self.t_initial = t_initial
        self.t_min = t_min
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations

    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        best_results: list[ScoredResult] = []

        for _ in range(n_grids):
            grid = self._random_grid()
            stars = self._random_stars()
            current_score = self._score(grid, stars or None)
            best = current_score
            t = self.t_initial

            for _ in range(self.max_iterations):
                if t < self.t_min:
                    break

                # Mutate either numbers or stars
                if stars and self.rng.random() < 0.3:
                    new_grid = grid
                    new_stars = self._star_neighbor(stars)
                else:
                    new_grid = self._neighbor(grid)
                    new_stars = stars

                neighbor_score = self._score(new_grid, new_stars or None)

                delta = neighbor_score.total_score - current_score.total_score

                if delta > 0 or self.rng.random() < np.exp(delta / t):
                    grid = new_grid
                    stars = new_stars
                    current_score = neighbor_score

                if current_score.total_score > best.total_score:
                    best = current_score

                t *= self.cooling_rate

            best_results.append(best)

        best_results.sort(key=lambda r: -r.total_score)

        # Deduplicate: keep diverse grids
        selected: list[ScoredResult] = []
        for r in best_results:
            if not any(r.numbers == s.numbers and r.stars == s.stars for s in selected):
                selected.append(r)
            if len(selected) >= n_grids:
                break

        # Fill gaps with mutations if not enough unique grids
        attempts = 0
        while len(selected) < n_grids and attempts < n_grids * 10:
            attempts += 1
            base = selected[0] if selected else best_results[0]
            new_grid = self._neighbor(base.numbers)
            new_stars = self._random_stars() if self._has_stars else []
            result = self._score(new_grid, new_stars or None)
            if not any(result.numbers == s.numbers and result.stars == s.stars for s in selected):
                selected.append(result)

        selected.sort(key=lambda r: -r.total_score)
        return selected[:n_grids]
