"""Hill Climbing optimizer with random restarts."""

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult

from .base import BaseOptimizer


class HillClimbing(BaseOptimizer):
    """Steepest-ascent Hill Climbing with random restarts."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        n_restarts: int = 100,
        max_no_improve: int = 50,
        seed: int | None = None,
    ):
        super().__init__(scorer, statistics, game, seed)
        self.n_restarts = n_restarts
        self.max_no_improve = max_no_improve

    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        all_results: list[ScoredResult] = []

        for _ in range(self.n_restarts):
            grid = self._random_grid()
            current = self._score(grid)
            no_improve = 0

            while no_improve < self.max_no_improve:
                neighbor = self._neighbor(grid)
                neighbor_score = self._score(neighbor)

                if neighbor_score.total_score > current.total_score:
                    grid = neighbor
                    current = neighbor_score
                    no_improve = 0
                else:
                    no_improve += 1

            all_results.append(current)

        all_results.sort(key=lambda r: -r.total_score)
        return all_results[:n_grids]
