"""Tabu Search optimizer."""

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult

from .base import BaseOptimizer


class TabuSearch(BaseOptimizer):
    """Explore neighborhoods while forbidding recently visited solutions."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        max_iterations: int = 10000,
        tabu_size: int = 100,
        n_neighbors: int = 20,
        seed: int | None = None,
    ):
        super().__init__(scorer, statistics, game, seed)
        self.max_iterations = max_iterations
        self.tabu_size = tabu_size
        self.n_neighbors = n_neighbors

    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        all_best: list[ScoredResult] = []

        for _ in range(n_grids):
            grid = self._random_grid()
            stars = self._random_stars()
            current = self._score(grid, stars or None)
            best = current
            tabu_list: list[tuple] = []

            for _ in range(self.max_iterations):
                # Generate neighbors
                neighbors: list[tuple[list[int], list[int], ScoredResult]] = []
                for _ in range(self.n_neighbors):
                    if stars and self.rng.random() < 0.3:
                        cand_grid = grid
                        cand_stars = self._star_neighbor(stars)
                    else:
                        cand_grid = self._neighbor(grid)
                        cand_stars = stars
                    key = (tuple(cand_grid), tuple(cand_stars))
                    if key not in tabu_list:
                        scored = self._score(cand_grid, cand_stars or None)
                        neighbors.append((cand_grid, cand_stars, scored))

                if not neighbors:
                    break

                # Pick the best non-tabu neighbor
                neighbors.sort(key=lambda x: -x[2].total_score)
                grid, stars, current = neighbors[0]

                # Update tabu list
                tabu_list.append((tuple(grid), tuple(stars)))
                if len(tabu_list) > self.tabu_size:
                    tabu_list.pop(0)

                if current.total_score > best.total_score:
                    best = current

            all_best.append(best)

        all_best.sort(key=lambda r: -r.total_score)
        return all_best
