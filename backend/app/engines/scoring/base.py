"""Base class for scoring criteria."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.game_definitions import GameConfig


class BaseScoringCriterion(ABC):
    """Abstract base for a scoring criterion returning a score in [0, 1]."""

    @abstractmethod
    def compute(self, grid: list[int], game: GameConfig, **kwargs: Any) -> float:
        """Compute criterion score for the given grid."""
        ...

    @abstractmethod
    def get_name(self) -> str: ...
