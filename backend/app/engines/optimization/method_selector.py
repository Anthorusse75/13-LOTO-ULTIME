"""Auto-selection of optimization method based on context."""

from math import comb

from app.core.game_definitions import GameConfig


def select_method(game: GameConfig, n_grids: int, time_budget: float = 5.0) -> str:
    """Choose the best optimization method given the search space and constraints."""
    space_size = comb(game.numbers_pool, game.numbers_drawn)

    if space_size < 100_000 and time_budget > 10 or n_grids <= 5 and time_budget > 5:
        return "simulated_annealing"
    elif n_grids >= 20:
        return "genetic"
    else:
        return "genetic"
