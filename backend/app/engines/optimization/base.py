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

    def _random_grid(self) -> list[int]:
        """Generate a random valid grid."""
        return sorted(
            self.rng.choice(
                range(self.game.min_number, self.game.max_number + 1),
                size=self.game.numbers_drawn,
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

    def _score(self, grid: list[int]) -> ScoredResult:
        """Score a grid using the scorer."""
        return self.scorer.score(grid, self.statistics, self.game)

    @abstractmethod
    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        """Run optimization and return the top n_grids results."""
