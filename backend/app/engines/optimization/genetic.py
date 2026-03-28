"""Genetic Algorithm optimizer."""

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult

from .base import BaseOptimizer


class GeneticAlgorithm(BaseOptimizer):
    """Evolve a population of grids using selection, crossover, and mutation."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        population_size: int = 200,
        max_generations: int = 500,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_size: int = 10,
        tournament_size: int = 3,
        seed: int | None = None,
    ):
        super().__init__(scorer, statistics, game, seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size

    def _crossover(self, parent1: list[int], parent2: list[int]) -> list[int]:
        """Uniform crossover: pick from the union of both parents."""
        combined = list(set(parent1) | set(parent2))
        if len(combined) < self.game.numbers_drawn:
            # Pad with random numbers if union is too small
            pool = [
                n
                for n in range(self.game.min_number, self.game.max_number + 1)
                if n not in combined
            ]
            combined.extend(
                self.rng.choice(
                    pool, size=self.game.numbers_drawn - len(combined), replace=False
                ).tolist()
            )
        return sorted(
            self.rng.choice(
                combined, size=self.game.numbers_drawn, replace=False
            ).tolist()
        )

    def _mutate(self, grid: list[int]) -> list[int]:
        """Mutate grid by replacing numbers with probability mutation_rate."""
        new_grid = grid.copy()
        for i in range(len(new_grid)):
            if self.rng.random() < self.mutation_rate:
                available = [
                    n
                    for n in range(self.game.min_number, self.game.max_number + 1)
                    if n not in new_grid
                ]
                new_grid[i] = int(self.rng.choice(available))
        return sorted(new_grid)

    def _tournament_select(
        self, population: list[ScoredResult]
    ) -> ScoredResult:
        """Select one individual via tournament selection."""
        indices = self.rng.choice(len(population), size=self.tournament_size, replace=False)
        candidates = [population[i] for i in indices]
        return max(candidates, key=lambda x: x.total_score)

    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        # Initialize population
        population: list[ScoredResult] = []
        for _ in range(self.population_size):
            grid = self._random_grid()
            population.append(self._score(grid))

        for _ in range(self.max_generations):
            # Sort by score descending
            population.sort(key=lambda x: -x.total_score)

            # Elitism: keep top
            new_pop = population[: self.elite_size]

            # Fill rest via crossover + mutation
            while len(new_pop) < self.population_size:
                parent1 = self._tournament_select(population)
                parent2 = self._tournament_select(population)

                if self.rng.random() < self.crossover_rate:
                    child_grid = self._crossover(parent1.numbers, parent2.numbers)
                else:
                    child_grid = parent1.numbers.copy()

                child_grid = self._mutate(child_grid)
                new_pop.append(self._score(child_grid))

            population = new_pop

        population.sort(key=lambda x: -x.total_score)
        return population[:n_grids]
