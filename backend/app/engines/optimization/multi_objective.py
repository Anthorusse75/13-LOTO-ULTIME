"""Multi-Objective optimizer (simplified NSGA-II)."""

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer, ScoredResult

from .base import BaseOptimizer


class MultiObjectiveOptimizer(BaseOptimizer):
    """NSGA-II inspired optimizer with 3 objectives: score, diversity, coverage."""

    def __init__(
        self,
        scorer: GridScorer,
        statistics: dict,
        game: GameConfig,
        population_size: int = 100,
        max_generations: int = 200,
        mutation_rate: float = 0.1,
        seed: int | None = None,
    ):
        super().__init__(scorer, statistics, game, seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate

    @staticmethod
    def _hamming_distance(g1: list[int], g2: list[int]) -> int:
        """Number of elements that differ between two sorted grids."""
        return len(set(g1) ^ set(g2))

    def _evaluate(self, results: list[ScoredResult]) -> list[tuple[float, float, float]]:
        """Compute 3 objectives for each individual: (score, diversity, coverage)."""
        objectives: list[tuple[float, float, float]] = []
        all_numbers: set[int] = set()
        for r in results:
            all_numbers.update(r.numbers)

        for i, r in enumerate(results):
            # Objective 1: total score
            score = r.total_score

            # Objective 2: diversity — average Hamming distance to others
            distances = [
                self._hamming_distance(r.numbers, other.numbers)
                for j, other in enumerate(results)
                if j != i
            ]
            max_dist = 2 * self.game.numbers_drawn
            diversity = (sum(distances) / len(distances) / max_dist) if distances else 0.0

            # Objective 3: coverage — unique numbers contribution
            unique_contribution = len(
                set(r.numbers) - {n for j, o in enumerate(results) if j != i for n in o.numbers}
            )
            coverage = unique_contribution / self.game.numbers_drawn

            objectives.append((score, diversity, coverage))

        return objectives

    def _dominates(
        self, obj_a: tuple[float, float, float], obj_b: tuple[float, float, float]
    ) -> bool:
        """Return True if a dominates b (at least as good on all, strictly better on at least one)."""
        at_least_one_better = False
        for a, b in zip(obj_a, obj_b):
            if a < b:
                return False
            if a > b:
                at_least_one_better = True
        return at_least_one_better

    def _non_dominated_sort(
        self,
        population: list[ScoredResult],
        objectives: list[tuple[float, float, float]],
    ) -> list[list[int]]:
        """Perform non-dominated sorting, returning fronts of indices."""
        n = len(population)
        domination_count = [0] * n
        dominated_set: list[list[int]] = [[] for _ in range(n)]
        fronts: list[list[int]] = [[]]

        for i in range(n):
            for j in range(i + 1, n):
                if self._dominates(objectives[i], objectives[j]):
                    dominated_set[i].append(j)
                    domination_count[j] += 1
                elif self._dominates(objectives[j], objectives[i]):
                    dominated_set[j].append(i)
                    domination_count[i] += 1

        for i in range(n):
            if domination_count[i] == 0:
                fronts[0].append(i)

        k = 0
        while fronts[k]:
            next_front: list[int] = []
            for i in fronts[k]:
                for j in dominated_set[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            k += 1
            fronts.append(next_front)

        # Remove empty trailing front
        return [f for f in fronts if f]

    def _crowding_distance(
        self, front_indices: list[int], objectives: list[tuple[float, float, float]]
    ) -> list[float]:
        """Compute crowding distance for individuals in a front."""
        n = len(front_indices)
        if n <= 2:
            return [float("inf")] * n

        distances = [0.0] * n
        num_objectives = 3

        for m in range(num_objectives):
            sorted_indices = sorted(range(n), key=lambda i: objectives[front_indices[i]][m])
            obj_min = objectives[front_indices[sorted_indices[0]]][m]
            obj_max = objectives[front_indices[sorted_indices[-1]]][m]
            obj_range = obj_max - obj_min

            distances[sorted_indices[0]] = float("inf")
            distances[sorted_indices[-1]] = float("inf")

            if obj_range > 0:
                for i in range(1, n - 1):
                    distances[sorted_indices[i]] += (
                        objectives[front_indices[sorted_indices[i + 1]]][m]
                        - objectives[front_indices[sorted_indices[i - 1]]][m]
                    ) / obj_range

        return distances

    def _mutate(self, grid: list[int]) -> list[int]:
        """Mutate by replacing one number with probability mutation_rate."""
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

    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        # Initialize population
        population: list[ScoredResult] = [
            self._score(self._random_grid(), self._random_stars() or None)
            for _ in range(self.population_size)
        ]

        for _ in range(self.max_generations):
            # Create offspring via mutation of random parents
            offspring: list[ScoredResult] = []
            for _ in range(self.population_size):
                parent = population[int(self.rng.integers(0, len(population)))]
                child_grid = self._mutate(parent.numbers)
                child_stars = self._star_neighbor(parent.stars or []) if self._has_stars else []
                offspring.append(self._score(child_grid, child_stars or None))

            combined = population + offspring
            objectives = self._evaluate(combined)

            # Non-dominated sorting
            fronts = self._non_dominated_sort(combined, objectives)

            # Select next population
            new_population: list[ScoredResult] = []
            for front_indices in fronts:
                if len(new_population) + len(front_indices) <= self.population_size:
                    new_population.extend(combined[i] for i in front_indices)
                else:
                    remaining = self.population_size - len(new_population)
                    crowding = self._crowding_distance(front_indices, objectives)
                    paired = sorted(zip(front_indices, crowding), key=lambda x: -x[1])
                    new_population.extend(combined[idx] for idx, _ in paired[:remaining])
                    break

            population = new_population

        # Return top n_grids by score
        population.sort(key=lambda r: -r.total_score)
        return population[:n_grids]
