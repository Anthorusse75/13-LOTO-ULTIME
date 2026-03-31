"""Auto-selection of optimization method based on context."""

from math import comb

from app.core.game_definitions import GameConfig


def select_method(game: GameConfig, n_grids: int, time_budget: float = 5.0) -> str:
    """Choose the best optimization method given the search space and constraints.

    Selection logic:
    - hill_climbing: fast local search for very small batches (1-3 grids)
    - tabu: systematic neighbourhood search for medium batches / moderate spaces
    - annealing: wider exploration for medium batches / large spaces (>10M combos)
    - genetic: population-based, natural fit for large batches (≥10 grids)
    """
    space_size = comb(game.numbers_pool, game.numbers_drawn)

    # Very small batch → fast greedy refinement
    if n_grids <= 3:
        return "hill_climbing"

    # Medium batch (4-9 grids)
    if n_grids < 10:
        # Large search space benefits from wider stochastic exploration
        if space_size > 10_000_000:
            return "annealing"
        return "tabu"

    # Large batch (≥10 grids) → population-based algorithm
    return "genetic"
