"""Wheeling engine orchestrator — combines greedy cover, coverage analysis,
cost estimation, gain scenarios, and star distribution.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

import structlog

from app.core.game_definitions import GameConfig

logger = structlog.get_logger(__name__)

from .cost_estimator import estimate_cost, estimate_grid_count
from .coverage import coverage_rate, full_wheel_size, reduction_rate, total_t_combinations
from .gain_analyzer import GainScenario, analyze_gains
from .greedy_cover import greedy_cover


@dataclass(frozen=True)
class WheelingPreviewResult:
    """Quick estimation returned before full generation."""

    estimated_grid_count: int
    estimated_cost: float
    total_t_combinations: int
    full_wheel_size: int
    reduction_rate_estimate: float


@dataclass(frozen=True)
class WheelingGrid:
    """A single grid in the wheeling system."""

    numbers: list[int]
    stars: list[int] | None = None


@dataclass(frozen=True)
class WheelingResult:
    """Full result of wheeling generation."""

    grids: list[WheelingGrid]
    grid_count: int
    total_cost: float
    coverage_rate: float
    reduction_rate: float
    total_t_combinations: int
    full_wheel_size: int
    computation_time_ms: float
    gain_scenarios: list[GainScenario] = field(default_factory=list)
    number_distribution: dict[int, int] = field(default_factory=dict)


class WheelingEngine:
    """Orchestrate wheeling system generation."""

    def __init__(self, game_config: GameConfig):
        self._config = game_config

    def preview(
        self,
        numbers: list[int],
        stars: list[int] | None,
        guarantee: int,
    ) -> WheelingPreviewResult:
        """Quick estimation without running the full algorithm."""
        n = len(numbers)
        k = self._config.numbers_drawn
        t = guarantee

        est_count = estimate_grid_count(n, k, t)

        # If stars generate combinatorial expansion, multiply
        if stars and self._config.stars_drawn:
            from math import comb
            star_combos = comb(len(stars), self._config.stars_drawn)
            est_count_with_stars = est_count * star_combos
        else:
            est_count_with_stars = est_count

        return WheelingPreviewResult(
            estimated_grid_count=est_count_with_stars,
            estimated_cost=estimate_cost(est_count_with_stars, self._config.grid_price),
            total_t_combinations=total_t_combinations(n, t),
            full_wheel_size=full_wheel_size(n, k),
            reduction_rate_estimate=reduction_rate(est_count, n, k),
        )

    def generate(
        self,
        numbers: list[int],
        stars: list[int] | None,
        guarantee: int,
        prize_tiers: list[dict[str, Any]] | None = None,
    ) -> WheelingResult:
        """Generate the full wheeling system.

        Parameters
        ----------
        numbers : list[int]
            User-selected main numbers.
        stars : list[int] | None
            User-selected stars/chance numbers (optional).
        guarantee : int
            Guarantee level *t*.
        prize_tiers : list[dict] | None
            Prize tier data for gain scenario analysis.
        """
        k = self._config.numbers_drawn
        t = guarantee
        start = time.perf_counter()

        # 1. Generate covering design for main numbers
        raw_grids = greedy_cover(numbers, k, t)

        # 2. Distribute stars across grids
        grids = self._distribute_stars(raw_grids, stars)

        grid_count = len(grids)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # 3. Metrics
        cov = coverage_rate(raw_grids, numbers, t)
        red = reduction_rate(len(raw_grids), len(numbers), k)
        total_t = total_t_combinations(len(numbers), t)
        fw_size = full_wheel_size(len(numbers), k)

        # 4. Number distribution
        dist: dict[int, int] = {}
        for g in grids:
            for num in g.numbers:
                dist[num] = dist.get(num, 0) + 1

        # 5. Gain scenarios (if prize tiers provided)
        gain_scenarios: list[GainScenario] = []
        if prize_tiers:
            gain_scenarios = analyze_gains(raw_grids, numbers, prize_tiers, k)

        cost = estimate_cost(grid_count, self._config.grid_price)

        logger.info(
            "wheeling_generated",
            game=self._config.slug,
            numbers_count=len(numbers),
            guarantee=t,
            grid_count=grid_count,
            coverage=round(cov, 4),
            reduction=round(red, 4),
            cost=cost,
            elapsed_ms=round(elapsed_ms, 1),
        )

        return WheelingResult(
            grids=grids,
            grid_count=grid_count,
            total_cost=cost,
            coverage_rate=cov,
            reduction_rate=red,
            total_t_combinations=total_t,
            full_wheel_size=fw_size,
            computation_time_ms=round(elapsed_ms, 1),
            gain_scenarios=gain_scenarios,
            number_distribution=dist,
        )

    def _distribute_stars(
        self,
        raw_grids: list[tuple[int, ...]],
        stars: list[int] | None,
    ) -> list[WheelingGrid]:
        """Attach stars to each grid.

        - No stars → just convert to WheelingGrid
        - Stars with stars_drawn: generate all star combinations,
          combine with number grids (for EuroMillions-style games)
          OR distribute cyclically (for Loto FDJ chance)
        """
        if not stars or not self._config.stars_drawn:
            return [WheelingGrid(numbers=list(g)) for g in raw_grids]

        stars_drawn = self._config.stars_drawn
        star_pool = sorted(stars)

        if len(star_pool) <= stars_drawn:
            # Only one star combination possible
            return [WheelingGrid(numbers=list(g), stars=star_pool) for g in raw_grids]

        star_combos = list(combinations(star_pool, stars_drawn))

        if self._config.stars_pool and self._config.stars_pool <= 10:
            # Small star pool (e.g. Loto FDJ chance 1–10): distribute cyclically
            grids: list[WheelingGrid] = []
            for i, g in enumerate(raw_grids):
                sc = list(star_combos[i % len(star_combos)])
                grids.append(WheelingGrid(numbers=list(g), stars=sc))
            return grids
        else:
            # Larger star pool (e.g. EuroMillions 1–12): combine all
            grids = []
            for g in raw_grids:
                for sc in star_combos:
                    grids.append(WheelingGrid(numbers=list(g), stars=list(sc)))
            return grids
