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
            stars = self._random_stars()
            current = self._score(grid, stars or None)
            no_improve = 0

            while no_improve < self.max_no_improve:
                if stars and self.rng.random() < 0.3:
                    new_grid = grid
                    new_stars = self._star_neighbor(stars)
                else:
                    new_grid = self._neighbor(grid)
                    new_stars = stars

                neighbor_score = self._score(new_grid, new_stars or None)

                if neighbor_score.total_score > current.total_score:
                    grid = new_grid
                    stars = new_stars
                    current = neighbor_score
                    no_improve = 0
                else:
                    no_improve += 1

            all_results.append(current)

        all_results.sort(key=lambda r: -r.total_score)

        # Deduplicate: keep diverse grids
        selected: list[ScoredResult] = []
        for r in all_results:
            if not any(r.numbers == s.numbers and r.stars == s.stars for s in selected):
                selected.append(r)
            if len(selected) >= n_grids:
                break

        # Fill gaps with mutations if not enough unique grids
        attempts = 0
        while len(selected) < n_grids and attempts < n_grids * 10:
            attempts += 1
            base = selected[0] if selected else all_results[0]
            new_grid = self._neighbor(base.numbers)
            new_stars = self._random_stars() if self._has_stars else []
            result = self._score(new_grid, new_stars or None)
            if not any(result.numbers == s.numbers and result.stars == s.stars for s in selected):
                selected.append(result)

        selected.sort(key=lambda r: -r.total_score)
        return selected[:n_grids]
