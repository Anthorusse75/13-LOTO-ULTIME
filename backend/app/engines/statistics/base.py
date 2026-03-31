"""Base class for all statistical engines."""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from app.core.game_definitions import GameConfig


class BaseStatisticsEngine(ABC):
    """Abstract base for statistical computation engines."""

    @abstractmethod
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict[int | str, Any]:
        """Compute statistics from a draw matrix.

        Args:
            draws: Matrix (N, k) of drawn numbers, ordered chronologically.
            game: Game configuration.

        Returns:
            Dictionary containing the computed statistics.
        """

    @abstractmethod
    def get_name(self) -> str:
        """Return the engine identifier name."""
