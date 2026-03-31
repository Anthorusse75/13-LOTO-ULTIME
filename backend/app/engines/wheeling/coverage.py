"""Coverage rate computation for wheeling systems."""

from itertools import combinations
from math import comb


def coverage_rate(
    grids: list[tuple[int, ...]],
    numbers: list[int],
    t: int,
) -> float:
    """Return the fraction of t-subsets of *numbers* covered by *grids*.

    Parameters
    ----------
    grids : list[tuple[int, ...]]
        The generated k-combinations.
    numbers : list[int]
        The user's selected numbers.
    t : int
        Guarantee level.

    Returns
    -------
    float
        Coverage rate in [0.0, 1.0].
    """
    sorted_nums = sorted(numbers)
    total = comb(len(sorted_nums), t)
    if total == 0:
        return 1.0

    covered: set[tuple[int, ...]] = set()
    for grid in grids:
        covered.update(combinations(grid, t))

    return len(covered) / total


def total_t_combinations(n: int, t: int) -> int:
    """Number of t-subsets in a set of n elements."""
    return comb(n, t)


def full_wheel_size(n: int, k: int) -> int:
    """Number of grids in a full wheel C(n, k)."""
    return comb(n, k)


def reduction_rate(grid_count: int, n: int, k: int) -> float:
    """Reduction compared to full wheel: (1 - grid_count / C(n,k)) × 100."""
    full = full_wheel_size(n, k)
    if full == 0:
        return 0.0
    return (1.0 - grid_count / full) * 100.0
