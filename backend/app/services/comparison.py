"""Comparison service — compare multiple strategies side by side."""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any

import numpy as np
import structlog

from app.core.game_definitions import GameConfig
from app.engines.wheeling.engine import WheelingEngine
from app.services.grid import GridService
from app.services.simulation import SimulationService

logger = structlog.get_logger(__name__)

STRATEGY_LABELS = {
    "top": "Top scoring",
    "portfolio": "Portefeuille diversifié",
    "random": "Aléatoire (baseline)",
    "wheeling": "Système réduit",
    "budget": "Budget optimisé",
    "profile": "Profil personnalisé",
    "method": "Méthode spécifique",
}


@dataclass
class StrategyResult:
    type: str
    label: str
    grids: list[dict[str, Any]]
    grid_count: int
    avg_score: float | None = None
    score_variance: float | None = None
    diversity: float | None = None
    coverage: float | None = None
    cost: float = 0.0
    robustness: float | None = None
    expected_gain: float | None = None


class ComparisonService:
    """Compare multiple lottery strategies on unified metrics."""

    def __init__(
        self,
        grid_service: GridService,
        simulation_service: SimulationService,
    ):
        self._grid_service = grid_service
        self._simulation_service = simulation_service

    async def compare(
        self,
        game_id: int,
        game: GameConfig,
        strategies: list[dict[str, Any]],
        include_gains: bool = False,
    ) -> dict[str, Any]:
        """Run all requested strategies, compute unified metrics, return comparison."""

        results: list[StrategyResult] = []

        # Run strategies concurrently
        tasks = []
        for strat in strategies:
            tasks.append(self._run_strategy(game_id, game, strat))

        strategy_results = await asyncio.gather(*tasks, return_exceptions=True)

        for strat, result in zip(strategies, strategy_results):
            if isinstance(result, Exception):
                logger.warning(
                    "comparison_strategy_failed",
                    strategy=strat.get("type"),
                    error=str(result),
                )
                # Add empty result for failed strategies
                results.append(StrategyResult(
                    type=strat.get("type", "unknown"),
                    label=STRATEGY_LABELS.get(strat.get("type", ""), strat.get("type", "unknown")),
                    grids=[],
                    grid_count=0,
                    cost=0.0,
                ))
            else:
                results.append(result)

        # Build summary
        summary = self._build_summary(results)

        return {
            "strategies": [
                {
                    "type": r.type,
                    "label": r.label,
                    "grid_count": r.grid_count,
                    "grids": r.grids[:10],  # limit to 10 grids in response
                    "avg_score": round(r.avg_score, 4) if r.avg_score is not None else None,
                    "score_variance": round(r.score_variance, 4) if r.score_variance is not None else None,
                    "diversity": round(r.diversity, 4) if r.diversity is not None else None,
                    "coverage": round(r.coverage, 4) if r.coverage is not None else None,
                    "cost": round(r.cost, 2),
                    "robustness": round(r.robustness, 4) if r.robustness is not None else None,
                    "expected_gain": round(r.expected_gain, 2) if r.expected_gain is not None else None,
                }
                for r in results
            ],
            "summary": summary,
        }

    async def _run_strategy(
        self,
        game_id: int,
        game: GameConfig,
        strategy: dict[str, Any],
    ) -> StrategyResult:
        """Execute a single strategy and compute its metrics."""

        stype = strategy["type"]
        count = strategy.get("count", 10)

        if stype == "top":
            return await self._run_top(game_id, game, count)
        elif stype == "portfolio":
            return await self._run_portfolio(game_id, game, count)
        elif stype == "random":
            return self._run_random(game, count)
        elif stype == "wheeling":
            return self._run_wheeling(
                game,
                strategy.get("numbers", []),
                strategy.get("stars"),
                strategy.get("guarantee", 3),
            )
        elif stype == "profile":
            return await self._run_profile(
                game_id, game, count, strategy.get("profile", "equilibre")
            )
        elif stype == "method":
            return await self._run_method(
                game_id, game, count, strategy.get("method", "annealing")
            )
        else:
            raise ValueError(f"Unknown strategy type: {stype}")

    async def _run_top(
        self, game_id: int, game: GameConfig, count: int
    ) -> StrategyResult:
        """Top scoring grids."""
        grids, method_used, _ = await self._grid_service.generate_grids(
            game_id=game_id, game=game, count=count
        )
        grid_dicts = [{"numbers": g.numbers, "stars": g.stars} for g in grids]
        scores = [g.total_score for g in grids]
        return self._build_result("top", grid_dicts, scores, game)

    async def _run_portfolio(
        self, game_id: int, game: GameConfig, count: int
    ) -> StrategyResult:
        """Diversified portfolio."""
        portfolio, _, _ = await self._grid_service.generate_portfolio(
            game_id=game_id, game=game, grid_count=count
        )
        grid_dicts = [{"numbers": g.numbers, "stars": g.stars} for g in portfolio.grids]
        scores = [g.total_score for g in portfolio.grids]
        result = self._build_result("portfolio", grid_dicts, scores, game)
        result.diversity = portfolio.diversity_score
        result.coverage = portfolio.coverage_score
        return result

    def _run_random(self, game: GameConfig, count: int) -> StrategyResult:
        """Random baseline grids."""
        rng = random.Random(42)
        grids: list[dict[str, Any]] = []
        for _ in range(count):
            numbers = sorted(rng.sample(range(1, game.max_number + 1), game.numbers_drawn))
            stars = None
            if game.stars_pool and game.stars_drawn:
                stars = sorted(rng.sample(range(1, game.stars_pool + 1), game.stars_drawn))
            grids.append({"numbers": numbers, "stars": stars})
        return self._build_result("random", grids, None, game)

    def _run_wheeling(
        self,
        game: GameConfig,
        numbers: list[int],
        stars: list[int] | None,
        guarantee: int,
    ) -> StrategyResult:
        """Wheeling system."""
        if len(numbers) < game.numbers_drawn:
            raise ValueError(
                f"Need at least {game.numbers_drawn} numbers for wheeling"
            )
        engine = WheelingEngine(game)
        result = engine.generate(numbers, stars, guarantee)
        grid_dicts = [{"numbers": g.numbers, "stars": g.stars} for g in result.grids]
        sr = self._build_result("wheeling", grid_dicts, None, game)
        sr.coverage = result.coverage_rate
        return sr

    async def _run_profile(
        self, game_id: int, game: GameConfig, count: int, profile: str
    ) -> StrategyResult:
        """Grids with a specific scoring profile."""
        grids, _, _ = await self._grid_service.generate_grids(
            game_id=game_id, game=game, count=count, profile=profile
        )
        grid_dicts = [{"numbers": g.numbers, "stars": g.stars} for g in grids]
        scores = [g.total_score for g in grids]
        result = self._build_result("profile", grid_dicts, scores, game)
        result.label = f"Profil {profile}"
        return result

    async def _run_method(
        self, game_id: int, game: GameConfig, count: int, method: str
    ) -> StrategyResult:
        """Grids with a specific optimization method."""
        grids, method_used, _ = await self._grid_service.generate_grids(
            game_id=game_id, game=game, count=count, method=method
        )
        grid_dicts = [{"numbers": g.numbers, "stars": g.stars} for g in grids]
        scores = [g.total_score for g in grids]
        result = self._build_result("method", grid_dicts, scores, game)
        result.label = f"Méthode {method_used}"
        return result

    def _build_result(
        self,
        stype: str,
        grids: list[dict[str, Any]],
        scores: list[float] | None,
        game: GameConfig,
    ) -> StrategyResult:
        """Build a StrategyResult with unified metrics."""
        label = STRATEGY_LABELS.get(stype, stype)
        grid_count = len(grids)
        cost = round(grid_count * game.grid_price, 2)

        avg_score = None
        score_variance = None
        if scores:
            arr = np.array(scores)
            avg_score = float(arr.mean())
            score_variance = float(arr.var())

        diversity = self._compute_diversity(grids) if grid_count >= 2 else None

        return StrategyResult(
            type=stype,
            label=label,
            grids=grids,
            grid_count=grid_count,
            avg_score=avg_score,
            score_variance=score_variance,
            diversity=diversity,
            cost=cost,
        )

    @staticmethod
    def _compute_diversity(grids: list[dict[str, Any]]) -> float:
        """Compute average pairwise Hamming distance normalized to [0,1]."""
        if len(grids) < 2:
            return 0.0

        number_sets = [set(g.get("numbers", [])) for g in grids]
        total_distance = 0.0
        pair_count = 0
        max_len = max(len(s) for s in number_sets) if number_sets else 1

        for i in range(len(number_sets)):
            for j in range(i + 1, len(number_sets)):
                common = len(number_sets[i] & number_sets[j])
                union = len(number_sets[i] | number_sets[j])
                if union > 0:
                    total_distance += 1.0 - (common / union)
                pair_count += 1

        return total_distance / pair_count if pair_count > 0 else 0.0

    @staticmethod
    def _build_summary(results: list[StrategyResult]) -> dict[str, Any]:
        """Build a textual summary comparing strategies."""
        valid = [r for r in results if r.grid_count > 0]
        if not valid:
            return {
                "best_score": None,
                "best_diversity": None,
                "best_coverage": None,
                "best_cost": None,
                "recommendation": "Aucune stratégie n'a produit de résultats.",
            }

        best_score = None
        best_diversity = None
        best_coverage = None
        best_cost = None

        scored = [r for r in valid if r.avg_score is not None]
        if scored:
            best = max(scored, key=lambda r: r.avg_score or 0)
            best_score = best.label

        diverse = [r for r in valid if r.diversity is not None]
        if diverse:
            best = max(diverse, key=lambda r: r.diversity or 0)
            best_diversity = best.label

        covered = [r for r in valid if r.coverage is not None]
        if covered:
            best = max(covered, key=lambda r: r.coverage or 0)
            best_coverage = best.label

        costed = [r for r in valid if r.cost > 0]
        if costed:
            best = min(costed, key=lambda r: r.cost)
            best_cost = best.label

        # Build recommendation text
        parts = []
        if best_score:
            parts.append(f"« {best_score} » obtient le meilleur score moyen")
        if best_diversity:
            parts.append(f"« {best_diversity} » offre la meilleure diversité")
        if best_coverage:
            parts.append(f"« {best_coverage} » maximise la couverture")
        if best_cost:
            parts.append(f"« {best_cost} » est la plus économique")

        recommendation = ". ".join(parts) + "." if parts else "Comparez les métriques pour choisir."

        return {
            "best_score": best_score,
            "best_diversity": best_diversity,
            "best_coverage": best_coverage,
            "best_cost": best_cost,
            "recommendation": recommendation,
        }
