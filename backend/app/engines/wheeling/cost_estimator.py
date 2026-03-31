"""Cost estimation for wheeling systems."""


def estimate_cost(grid_count: int, grid_price: float) -> float:
    """Total cost = number of grids × price per grid."""
    return round(grid_count * grid_price, 2)


def estimate_grid_count(n: int, k: int, t: int) -> int:
    """Quick heuristic estimate of the number of grids needed.

    Uses a rough formula based on the Schönheim bound / empirical ratios.
    This is for the *preview* step (before running the full algorithm).
    """
    from math import comb, ceil

    total_t = comb(n, t)
    t_per_grid = comb(k, t)
    if t_per_grid == 0:
        return 1
    # Greedy typically needs ~ln(total_t) ratio → use a 1.2x multiplier
    lower_bound = ceil(total_t / t_per_grid)
    return max(lower_bound, 1)
