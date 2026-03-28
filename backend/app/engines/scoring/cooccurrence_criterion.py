"""Cooccurrence scoring criterion."""

from app.core.game_definitions import GameConfig

from .base import BaseScoringCriterion


class CooccurrenceCriterion(BaseScoringCriterion):
    """Score based on pair affinities — favours historically co-drawn numbers."""

    def compute(self, grid: list[int], game: GameConfig, **kwargs) -> float:
        cooccurrences: dict = kwargs["cooccurrences"]
        pairs = cooccurrences.get("pairs", {})

        all_affinities = [v["affinity"] for v in pairs.values()]
        if not all_affinities:
            return 0.5

        min_a, max_a = min(all_affinities), max(all_affinities)
        range_a = max_a - min_a if max_a > min_a else 1.0

        pair_scores = []
        sorted_grid = sorted(grid)
        for i in range(len(sorted_grid)):
            for j in range(i + 1, len(sorted_grid)):
                key = f"{sorted_grid[i]}-{sorted_grid[j]}"
                if key in pairs:
                    affinity = pairs[key]["affinity"]
                    pair_scores.append((affinity - min_a) / range_a)
                else:
                    pair_scores.append(0.5)

        return sum(pair_scores) / len(pair_scores) if pair_scores else 0.5

    def get_name(self) -> str:
        return "cooccurrence"
