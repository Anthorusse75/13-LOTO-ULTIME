"""Frequency scoring criterion."""

from typing import Any

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class FrequencyCriterion(BaseScoringCriterion):
    """Score based on frequency ratios — favours frequently drawn numbers."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs: Any) -> float:
        frequencies: dict[str, Any] = kwargs["frequencies"]
        all_ratios = [
            frequencies[str(n)]["ratio"]
            for n in range(game.min_number, game.max_number + 1)
            if str(n) in frequencies
        ]
        if not all_ratios:
            return 0.5

        min_r, max_r = min(all_ratios), max(all_ratios)
        if max_r == min_r:
            # All frequencies identical → neutral score
            return 0.5
        range_r = max_r - min_r

        normalized = []
        for num in grid:
            key = str(num)
            if key in frequencies:
                ratio = frequencies[key]["ratio"]
                normalized.append((ratio - min_r) / range_r)
            else:
                normalized.append(0.0)

        return float(sum(normalized) / len(normalized))

    def get_name(self) -> str:
        return "frequency"
