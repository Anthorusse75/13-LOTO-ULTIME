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
            current = self._score(grid)
            best = current
            tabu_list: list[tuple[int, ...]] = []

            for _ in range(self.max_iterations):
                # Generate neighbors
                neighbors: list[tuple[list[int], ScoredResult]] = []
                for _ in range(self.n_neighbors):
                    candidate = self._neighbor(grid)
                    key = tuple(candidate)
                    if key not in tabu_list:
                        scored = self._score(candidate)
                        neighbors.append((candidate, scored))

                if not neighbors:
                    break

                # Pick the best non-tabu neighbor
                neighbors.sort(key=lambda x: -x[1].total_score)
                grid, current = neighbors[0]

                # Update tabu list
                tabu_list.append(tuple(grid))
                if len(tabu_list) > self.tabu_size:
                    tabu_list.pop(0)

                if current.total_score > best.total_score:
                    best = current

            all_best.append(best)

        all_best.sort(key=lambda r: -r.total_score)
        return all_best
