"""Monte Carlo simulation engine for lottery grids and portfolios."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import hypergeom

from app.core.game_definitions import GameConfig


@dataclass
class SimulationResult:
    """Result of Monte Carlo simulation for a single grid."""

    grid: list[int]
    stars: list[int] | None
    n_simulations: int
    match_distribution: dict[int, int]
    star_match_distribution: dict[int, int] | None
    avg_matches: float
    expected_matches: float


@dataclass
class PortfolioSimulationResult:
    """Result of Monte Carlo simulation for a portfolio."""

    n_simulations: int
    hit_rate: float
    min_matches_threshold: int
    best_match_distribution: dict[int, int]
    avg_best_matches: float


class MonteCarloSimulator:
    """Simulate random draws and measure grid/portfolio performance."""

    def __init__(self, game: GameConfig, seed: int | None = None):
        self.game = game
        self.rng = np.random.default_rng(seed)

    def simulate_grid(
        self,
        grid: list[int],
        stars: list[int] | None = None,
        n_simulations: int = 10_000,
    ) -> SimulationResult:
        """Simulate n_simulations random draws and count matches for a grid."""
        k = self.game.numbers_drawn
        numbers = np.arange(self.game.min_number, self.game.max_number + 1)
        grid_set = set(grid)

        match_counts = np.zeros(k + 1, dtype=int)

        for _ in range(n_simulations):
            draw = set(self.rng.choice(numbers, size=k, replace=False).tolist())
            matches = len(grid_set & draw)
            match_counts[matches] += 1

        # Star simulation
        star_match_counts = None
        if self.game.stars_pool and self.game.stars_drawn and stars:
            s = self.game.stars_drawn
            star_numbers = np.arange(1, self.game.stars_pool + 1)
            star_match_counts = np.zeros(s + 1, dtype=int)
            star_set = set(stars)

            for _ in range(n_simulations):
                draw_stars = set(self.rng.choice(star_numbers, size=s, replace=False).tolist())
                star_matches = len(star_set & draw_stars)
                star_match_counts[star_matches] += 1

        # Compute avg matches
        indices = np.arange(k + 1)
        avg_matches = float(np.average(indices, weights=match_counts))

        # Theoretical expected matches (hypergeometric mean)
        n = self.game.max_number - self.game.min_number + 1
        expected_matches = k * k / n

        return SimulationResult(
            grid=sorted(grid),
            stars=sorted(stars) if stars else None,
            n_simulations=n_simulations,
            match_distribution={i: int(match_counts[i]) for i in range(k + 1)},
            star_match_distribution=(
                {i: int(star_match_counts[i]) for i in range(self.game.stars_drawn + 1)}
                if star_match_counts is not None
                else None
            ),
            avg_matches=round(avg_matches, 6),
            expected_matches=round(expected_matches, 6),
        )

    def simulate_portfolio(
        self,
        portfolio: list[list[int]],
        n_simulations: int = 10_000,
        min_matches: int = 2,
    ) -> PortfolioSimulationResult:
        """Simulate draws and measure how often at least one grid hits."""
        k = self.game.numbers_drawn
        numbers = np.arange(self.game.min_number, self.game.max_number + 1)
        portfolio_sets = [set(g) for g in portfolio]

        hits = 0
        best_match_counts = np.zeros(k + 1, dtype=int)

        for _ in range(n_simulations):
            draw = set(self.rng.choice(numbers, size=k, replace=False).tolist())

            best = 0
            for g_set in portfolio_sets:
                m = len(g_set & draw)
                if m > best:
                    best = m

            best_match_counts[best] += 1
            if best >= min_matches:
                hits += 1

        indices = np.arange(k + 1)
        avg_best = float(np.average(indices, weights=best_match_counts))

        return PortfolioSimulationResult(
            n_simulations=n_simulations,
            hit_rate=round(hits / n_simulations, 6) if n_simulations > 0 else 0.0,
            min_matches_threshold=min_matches,
            best_match_distribution={i: int(best_match_counts[i]) for i in range(k + 1)},
            avg_best_matches=round(avg_best, 6),
        )

    @staticmethod
    def theoretical_distribution(n: int, k: int) -> dict[int, float]:
        """Compute theoretical hypergeometric probabilities P(X=m) for m=0..k.

        n = pool size, k = numbers drawn.
        """
        rv = hypergeom(n, k, k)
        return {m: round(float(rv.pmf(m)), 10) for m in range(k + 1)}
