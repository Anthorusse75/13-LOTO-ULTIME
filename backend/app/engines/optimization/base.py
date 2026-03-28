"""Abstract base class for optimization meta-heuristics."""

from abc import ABC, abstractmethod

import numpy as np

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult


class BaseOptimizer(ABC):
    """Base class for all optimization algorithms."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        seed: int | None = None,
    ):
        self.scorer = scorer
        self.statistics = statistics
        self.game = game
        self.rng = np.random.default_rng(seed)
        self._has_stars = bool(game.stars_pool and game.stars_drawn)

    def _random_grid(self) -> list[int]:
        """Generate a random valid grid."""
        return sorted(
            self.rng.choice(
                range(self.game.min_number, self.game.max_number + 1),
                size=self.game.numbers_drawn,
                replace=False,
            ).tolist()
        )

    def _random_stars(self) -> list[int]:
        """Generate random stars (empty list if game has no stars)."""
        if not self._has_stars:
            return []
        return sorted(
            self.rng.choice(
                range(1, self.game.stars_pool + 1),
                size=self.game.stars_drawn,
                replace=False,
            ).tolist()
        )

    def _neighbor(self, grid: list[int]) -> list[int]:
        """Generate a neighbor by replacing one random number."""
        new_grid = grid.copy()
        idx = self.rng.integers(0, len(new_grid))
        available = [
            n for n in range(self.game.min_number, self.game.max_number + 1) if n not in new_grid
        ]
        new_grid[idx] = int(self.rng.choice(available))
        return sorted(new_grid)

    def _star_neighbor(self, stars: list[int]) -> list[int]:
        """Generate a star neighbor by replacing one random star."""
        if not stars:
            return stars
        new_stars = stars.copy()
        idx = self.rng.integers(0, len(new_stars))
        available = [n for n in range(1, self.game.stars_pool + 1) if n not in new_stars]
        new_stars[idx] = int(self.rng.choice(available))
        return sorted(new_stars)

    def _score(self, grid: list[int], stars: list[int] | None = None) -> ScoredResult:
        """Score a grid (with optional stars) using the scorer."""
        if stars and self._has_stars:
            return self.scorer.score_with_stars(grid, stars, self.statistics, self.game)
        return self.scorer.score(grid, self.statistics, self.game)

    @abstractmethod
    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        """Run optimization and return the top n_grids results."""
