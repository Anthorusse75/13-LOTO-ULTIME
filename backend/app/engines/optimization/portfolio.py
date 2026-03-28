"""Portfolio optimizer — select a diverse, high-quality set of grids."""

from dataclasses import dataclass

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import ScoredResult


STRATEGY_WEIGHTS: dict[str, tuple[float, float, float, float]] = {
    "balanced": (0.30, 0.25, 0.25, 0.20),
    "max_diversity": (0.15, 0.45, 0.25, 0.15),
    "max_coverage": (0.15, 0.15, 0.55, 0.15),
    "min_correlation": (0.20, 0.20, 0.20, 0.40),
}


@dataclass
class PortfolioResult:
    """Result of portfolio optimization."""

    grids: list[ScoredResult]
    strategy: str
    diversity_score: float
    coverage_score: float
    avg_grid_score: float
    min_hamming_distance: float


class PortfolioOptimizer:
    """Greedy portfolio construction maximizing composite F(P) objective."""

    def __init__(self, game: GameConfig):
        self.game = game

    @staticmethod
    def _hamming_distance(g1: list[int], g2: list[int]) -> int:
        """Number of elements that differ between two sorted grids."""
        return len(set(g1) ^ set(g2))

    def _marginal_value(
        self,
        portfolio: list[ScoredResult],
        candidate: ScoredResult,
        weights: tuple[float, float, float, float],
    ) -> float:
        """Compute the marginal value of adding candidate to the portfolio."""
        w_score, w_div, w_cov, w_corr = weights
        max_dist = 2 * self.game.numbers_drawn

        # Score component
        score_component = w_score * candidate.total_score

        # Diversity: min Hamming distance to existing grids (normalized)
        min_dist = min(
            self._hamming_distance(candidate.numbers, g.numbers) for g in portfolio
        )
        diversity_component = w_div * (min_dist / max_dist)

        # Coverage: new numbers brought in (normalized)
        existing_numbers: set[int] = set()
        for g in portfolio:
            existing_numbers.update(g.numbers)
        new_numbers = len(set(candidate.numbers) - existing_numbers)
        coverage_component = w_cov * (new_numbers / self.game.numbers_drawn)

        # Anti-correlation: max overlap with any existing grid (penalty)
        max_overlap = max(
            len(set(candidate.numbers) & set(g.numbers)) for g in portfolio
        )
        correlation_component = w_corr * (max_overlap / self.game.numbers_drawn)

        return score_component + diversity_component + coverage_component - correlation_component

    def _compute_metrics(
        self, grids: list[ScoredResult]
    ) -> tuple[float, float, float, float]:
        """Return (diversity_score, coverage_score, avg_score, min_hamming)."""
        if not grids:
            return (0.0, 0.0, 0.0, 0.0)

        # Average score
        avg_score = sum(g.total_score for g in grids) / len(grids)

        # Coverage (unique numbers / pool)
        all_numbers: set[int] = set()
        for g in grids:
            all_numbers.update(g.numbers)
        coverage = len(all_numbers) / self.game.numbers_pool

        # Min Hamming distance between any two grids
        max_dist = 2 * self.game.numbers_drawn
        min_ham = float("inf")
        for i in range(len(grids)):
            for j in range(i + 1, len(grids)):
                d = self._hamming_distance(grids[i].numbers, grids[j].numbers)
                if d < min_ham:
                    min_ham = d

        if min_ham == float("inf"):
            min_ham = 0.0

        # Diversity: normalized average pairwise distance
        total_dist = 0.0
        count = 0
        for i in range(len(grids)):
            for j in range(i + 1, len(grids)):
                total_dist += self._hamming_distance(grids[i].numbers, grids[j].numbers)
                count += 1
        diversity = (total_dist / count / max_dist) if count > 0 else 0.0

        return (diversity, coverage, avg_score, min_ham)

    def optimize(
        self,
        candidate_grids: list[ScoredResult],
        target_size: int,
        strategy: str = "balanced",
    ) -> PortfolioResult:
        """Build an optimized portfolio from candidates using greedy selection."""
        if strategy not in STRATEGY_WEIGHTS:
            raise ValueError(
                f"Unknown strategy '{strategy}'. Available: {list(STRATEGY_WEIGHTS.keys())}"
            )

        weights = STRATEGY_WEIGHTS[strategy]

        if not candidate_grids:
            return PortfolioResult(
                grids=[], strategy=strategy,
                diversity_score=0.0, coverage_score=0.0,
                avg_grid_score=0.0, min_hamming_distance=0.0,
            )

        # Sort candidates by score descending, start with the best
        sorted_candidates = sorted(candidate_grids, key=lambda r: -r.total_score)
        portfolio: list[ScoredResult] = [sorted_candidates[0]]
        remaining = sorted_candidates[1:]

        while len(portfolio) < target_size and remaining:
            best_candidate = None
            best_value = -float("inf")

            for candidate in remaining:
                value = self._marginal_value(portfolio, candidate, weights)
                if value > best_value:
                    best_value = value
                    best_candidate = candidate

            if best_candidate is None:
                break

            portfolio.append(best_candidate)
            remaining.remove(best_candidate)

        diversity, coverage, avg_score, min_ham = self._compute_metrics(portfolio)

        return PortfolioResult(
            grids=portfolio,
            strategy=strategy,
            diversity_score=round(diversity, 4),
            coverage_score=round(coverage, 4),
            avg_grid_score=round(avg_score, 6),
            min_hamming_distance=round(min_ham, 1),
        )
