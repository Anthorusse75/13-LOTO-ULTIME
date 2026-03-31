"""Gain scenario analysis for wheeling systems.

Given a set of wheeling grids and prize tier data, compute optimistic /
average / pessimistic gain scenarios for each prize rank.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any


@dataclass(frozen=True)
class GainScenario:
    """Gain analysis for a single prize rank."""

    rank: int
    name: str
    match_numbers: int
    match_stars: int
    avg_prize: float
    matching_grids_best: int      # optimistic: max grids matching this rank
    matching_grids_avg: float     # average across possible draws
    matching_grids_worst: int     # pessimistic: min grids if at least 1 matches
    potential_gain_best: float
    potential_gain_avg: float
    potential_gain_worst: float


def _count_matches(
    grid_numbers: tuple[int, ...],
    drawn_numbers: tuple[int, ...],
) -> int:
    """Count how many numbers in *grid_numbers* appear in *drawn_numbers*."""
    return len(set(grid_numbers) & set(drawn_numbers))


def analyze_gains(
    grids: list[tuple[int, ...]],
    selected_numbers: list[int],
    prize_tiers: list[dict[str, Any]],
    k: int,
) -> list[GainScenario]:
    """Compute gain scenarios for each prize tier.

    Parameters
    ----------
    grids : list[tuple[int, ...]]
        The wheeling system grids (numbers only).
    selected_numbers : list[int]
        The user's selected numbers.
    prize_tiers : list[dict]
        Prize tiers from DB: {rank, name, match_numbers, match_stars, avg_prize, probability}.
    k : int
        Numbers per grid.

    Returns
    -------
    list[GainScenario]
        One scenario per prize tier, sorted by rank.
    """
    sorted_nums = sorted(selected_numbers)
    n = len(sorted_nums)
    scenarios: list[GainScenario] = []

    for tier in sorted(prize_tiers, key=lambda t: t["rank"]):
        req = tier["match_numbers"]

        if req > k or req > n:
            scenarios.append(GainScenario(
                rank=tier["rank"],
                name=tier["name"],
                match_numbers=req,
                match_stars=tier.get("match_stars", 0),
                avg_prize=tier["avg_prize"],
                matching_grids_best=0,
                matching_grids_avg=0.0,
                matching_grids_worst=0,
                potential_gain_best=0.0,
                potential_gain_avg=0.0,
                potential_gain_worst=0.0,
            ))
            continue

        # Simulate: for each possible drawn set of k numbers from selected_numbers,
        # count how many wheeling grids match >= req numbers
        # This is expensive for large n — sample if needed
        drawn_combos = list(combinations(sorted_nums, k))
        match_counts: list[int] = []

        for drawn in drawn_combos:
            drawn_set = set(drawn)
            count = 0
            for grid in grids:
                if len(set(grid) & drawn_set) >= req:
                    count += 1
            match_counts.append(count)

        non_zero = [c for c in match_counts if c > 0]
        best = max(match_counts) if match_counts else 0
        avg = sum(match_counts) / len(match_counts) if match_counts else 0.0
        worst = min(non_zero) if non_zero else 0

        prize = tier["avg_prize"]
        scenarios.append(GainScenario(
            rank=tier["rank"],
            name=tier["name"],
            match_numbers=req,
            match_stars=tier.get("match_stars", 0),
            avg_prize=prize,
            matching_grids_best=best,
            matching_grids_avg=round(avg, 2),
            matching_grids_worst=worst,
            potential_gain_best=round(best * prize, 2),
            potential_gain_avg=round(avg * prize, 2),
            potential_gain_worst=round(worst * prize, 2),
        ))

    return scenarios
