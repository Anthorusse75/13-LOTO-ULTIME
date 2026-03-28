"""Frequency scoring criterion."""

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class FrequencyCriterion(BaseScoringCriterion):
    """Score based on frequency ratios — favours frequently drawn numbers."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs) -> float:
        frequencies: dict = kwargs["frequencies"]
        all_ratios = [
            frequencies[str(n)]["ratio"]
            for n in range(game.min_number, game.max_number + 1)
            if str(n) in frequencies
        ]
        if not all_ratios:
            return 0.5

        min_r, max_r = min(all_ratios), max(all_ratios)
        range_r = max_r - min_r if max_r > min_r else 1.0

        normalized = []
        for num in grid:
            key = str(num)
            if key in frequencies:
                ratio = frequencies[key]["ratio"]
                normalized.append((ratio - min_r) / range_r)
            else:
                normalized.append(0.0)

        return sum(normalized) / len(normalized)

    def get_name(self) -> str:
        return "frequency"
