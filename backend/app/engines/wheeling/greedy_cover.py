"""Greedy Set Cover algorithm for covering design C(n, k, t).

Generates a minimal(-ish) set of k-combinations from *numbers* such that
every t-subset of *numbers* appears in at least one combination.
"""

from itertools import combinations


def greedy_cover(
    numbers: list[int],
    k: int,
    t: int,
    *,
    max_iterations: int = 100_000,
) -> list[tuple[int, ...]]:
    """Build a covering design using the greedy Set Cover approximation.

    Parameters
    ----------
    numbers : list[int]
        The user's selected numbers (|numbers| = n).
    k : int
        Numbers per grid (e.g. 5 for Loto FDJ).
    t : int
        Guarantee level – every t-subset of *numbers* will appear in >= 1 grid.
    max_iterations : int
        Safety cap to avoid runaway computation.

    Returns
    -------
    list[tuple[int, ...]]
        The selected k-combinations (each sorted).

    Raises
    ------
    ValueError
        If inputs are invalid (n < k, t > k, t < 2, etc.).
    """
    n = len(numbers)
    if n < k:
        raise ValueError(f"Need at least k={k} numbers, got {n}")
    if t < 2 or t > k:
        raise ValueError(f"Guarantee t must be in [2, k={k}], got {t}")
    if n == k:
        return [tuple(sorted(numbers))]

    sorted_nums = sorted(numbers)

    # Universe of t-subsets that must be covered
    universe: set[tuple[int, ...]] = set(combinations(sorted_nums, t))

    # Pre-compute all candidate k-combinations and their t-subsets
    candidates: list[tuple[tuple[int, ...], set[tuple[int, ...]]]] = []
    for combo in combinations(sorted_nums, k):
        t_subs = set(combinations(combo, t))
        candidates.append((combo, t_subs))

    selected: list[tuple[int, ...]] = []
    iteration = 0

    while universe and iteration < max_iterations:
        iteration += 1
        # Pick the candidate that covers the most remaining t-subsets
        best_combo: tuple[int, ...] | None = None
        best_covered: set[tuple[int, ...]] = set()
        best_count = 0

        for combo, t_subs in candidates:
            covered = t_subs & universe
            count = len(covered)
            if count > best_count:
                best_count = count
                best_combo = combo
                best_covered = covered
            if count == len(t_subs):
                # Can't do better than full coverage for this combo
                break

        if best_combo is None or best_count == 0:
            break

        selected.append(best_combo)
        universe -= best_covered

    return selected
