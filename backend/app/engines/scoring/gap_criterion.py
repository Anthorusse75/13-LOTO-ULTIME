"""Gap (retard) scoring criterion."""

import math
from typing import Any

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class GapCriterion(BaseScoringCriterion):
    """Score based on gap analysis — favours numbers that are 'overdue'."""

    def __init__(self, sensitivity: float = 3.0):
        self.sensitivity = sensitivity

    def compute(self, grid: list[int], game: GameConfig, **kwargs: Any) -> float:
        gaps: dict[str, Any] = kwargs["gaps"]
        scores = []
        for num in grid:
            key = str(num)
            if key not in gaps:
                scores.append(0.5)
                continue
            gap_data = gaps[key]
            current = gap_data["current_gap"]
            avg = gap_data["avg_gap"]

            if avg > 0:
                ratio = (current - avg) / avg
                score = 1.0 / (1.0 + math.exp(-self.sensitivity * ratio))
            else:
                score = 0.5
            scores.append(score)

        return sum(scores) / len(scores)

    def get_name(self) -> str:
        return "gap"
