"""Budget service — optimize grid allocation within a given budget."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_definitions import GameConfig
from app.engines.budget import (
    BudgetOptimizationResult,
    BudgetRecommendation,
    GainScenarioSummary,
    compute_max_grids,
    rank_recommendations,
)
from app.engines.wheeling.engine import WheelingEngine
from app.models.budget import BudgetPlan
from app.repositories.budget_repository import BudgetRepository
from app.services.grid import GridService

logger = structlog.get_logger(__name__)


class BudgetService:
    def __init__(
        self,
        repo: BudgetRepository,
        grid_service: GridService,
        session: AsyncSession,
    ):
        self._repo = repo
        self._grid_service = grid_service
        self._session = session

    async def optimize(
        self,
        game_id: int,
        game_config: GameConfig,
        user_id: int,
        budget: float,
        objective: str,
        numbers: list[int] | None = None,
    ) -> tuple[BudgetOptimizationResult, BudgetPlan]:
        grid_price = game_config.grid_price
        max_grids = compute_max_grids(budget, grid_price)

        if max_grids < 1:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=422,
                detail=f"Budget insuffisant : prix d'une grille = {grid_price}€",
            )

        recommendations: list[BudgetRecommendation] = []

        # ── Strategy 1 : top scored grids ──
        try:
            top_rec = await self._build_top_strategy(game_id, game_config, max_grids)
            recommendations.append(top_rec)
        except Exception:
            logger.warning("budget_top_strategy_failed", exc_info=True)

        # ── Strategy 2 : diversified portfolio ──
        try:
            portfolio_rec = await self._build_portfolio_strategy(
                game_id, game_config, max_grids
            )
            recommendations.append(portfolio_rec)
        except Exception:
            logger.warning("budget_portfolio_strategy_failed", exc_info=True)

        # ── Strategy 3 : wheeling (only if enough numbers supplied) ──
        if numbers and len(numbers) >= game_config.numbers_drawn + 1:
            try:
                wheeling_rec = self._build_wheeling_strategy(
                    game_config, numbers, max_grids, grid_price
                )
                recommendations.append(wheeling_rec)
            except Exception:
                logger.warning("budget_wheeling_strategy_failed", exc_info=True)

        # ── Rank & mark recommended ──
        recommendations = rank_recommendations(recommendations, objective)

        result = BudgetOptimizationResult(
            budget=budget,
            grid_price=grid_price,
            max_grids=max_grids,
            recommendations=recommendations,
        )

        # ── Persist ──
        plan = BudgetPlan(
            user_id=user_id,
            game_id=game_id,
            budget=budget,
            objective=objective,
            selected_numbers=numbers,
            recommendations=[
                {
                    "strategy": r.strategy,
                    "grids": r.grids,
                    "grid_count": r.grid_count,
                    "total_cost": r.total_cost,
                    "avg_score": r.avg_score,
                    "diversity_score": r.diversity_score,
                    "coverage_rate": r.coverage_rate,
                    "expected_gain": {
                        "optimistic": r.expected_gain.optimistic,
                        "mean": r.expected_gain.mean,
                        "pessimistic": r.expected_gain.pessimistic,
                    },
                    "explanation": r.explanation,
                    "is_recommended": r.is_recommended,
                }
                for r in recommendations
            ],
        )
        plan = await self._repo.create(plan)
        return result, plan

    # ── Strategy builders ──

    async def _build_top_strategy(
        self,
        game_id: int,
        game_config: GameConfig,
        max_grids: int,
    ) -> BudgetRecommendation:
        grids, _, _ = await self._grid_service.generate_grids(
            game_id=game_id,
            game=game_config,
            count=max_grids,
        )
        avg_score = sum(g.total_score for g in grids) / len(grids) if grids else 0.0
        grid_dicts = [
            {"numbers": g.numbers, "stars": g.stars} for g in grids
        ]
        return BudgetRecommendation(
            strategy="top",
            grids=grid_dicts,
            grid_count=len(grids),
            total_cost=round(len(grids) * game_config.grid_price, 2),
            avg_score=round(avg_score, 2),
            diversity_score=None,
            coverage_rate=None,
            expected_gain=GainScenarioSummary(
                optimistic=round(avg_score * len(grids) * 0.15, 2),
                mean=round(avg_score * len(grids) * 0.05, 2),
                pessimistic=0.0,
            ),
            explanation=(
                "Sélectionne les grilles ayant les meilleurs scores individuels. "
                "Maximise la qualité moyenne mais peut manquer de diversité."
            ),
        )

    async def _build_portfolio_strategy(
        self,
        game_id: int,
        game_config: GameConfig,
        max_grids: int,
    ) -> BudgetRecommendation:
        portfolio, _, _ = await self._grid_service.generate_portfolio(
            game_id=game_id,
            game=game_config,
            grid_count=max_grids,
            strategy="balanced",
        )
        grid_dicts = [
            {"numbers": g.numbers, "stars": g.stars} for g in portfolio.grids
        ]
        return BudgetRecommendation(
            strategy="portfolio",
            grids=grid_dicts,
            grid_count=len(portfolio.grids),
            total_cost=round(len(portfolio.grids) * game_config.grid_price, 2),
            avg_score=round(portfolio.avg_grid_score, 2),
            diversity_score=round(portfolio.diversity_score, 4),
            coverage_rate=round(portfolio.coverage_score, 4),
            expected_gain=GainScenarioSummary(
                optimistic=round(portfolio.avg_grid_score * len(portfolio.grids) * 0.12, 2),
                mean=round(portfolio.avg_grid_score * len(portfolio.grids) * 0.04, 2),
                pessimistic=0.0,
            ),
            explanation=(
                "Portefeuille diversifié qui équilibre qualité et couverture numérique. "
                "Réduit le risque de chevauchement entre les grilles."
            ),
        )

    def _build_wheeling_strategy(
        self,
        game_config: GameConfig,
        numbers: list[int],
        max_grids: int,
        grid_price: float,
    ) -> BudgetRecommendation:
        engine = WheelingEngine(game_config)
        k = game_config.numbers_drawn

        # Find best guarantee level that fits in budget
        best_guarantee = 2
        for t in range(min(k, 4), 1, -1):
            preview = engine.preview(numbers, None, t)
            if preview.estimated_grid_count <= max_grids:
                best_guarantee = t
                break

        result = engine.generate(numbers, None, best_guarantee)
        actual_count = min(result.grid_count, max_grids)
        grid_dicts = [
            {"numbers": g.numbers, "stars": g.stars}
            for g in result.grids[:actual_count]
        ]
        return BudgetRecommendation(
            strategy="wheeling",
            grids=grid_dicts,
            grid_count=actual_count,
            total_cost=round(actual_count * grid_price, 2),
            avg_score=None,
            diversity_score=None,
            coverage_rate=round(result.coverage_rate, 4),
            expected_gain=GainScenarioSummary(
                optimistic=round(result.coverage_rate * actual_count * grid_price * 2.0, 2),
                mean=round(result.coverage_rate * actual_count * grid_price * 0.5, 2),
                pessimistic=0.0,
            ),
            explanation=(
                f"Système réduit (garantie {best_guarantee}/{k}) couvrant "
                f"{round(result.coverage_rate * 100, 1)}% des combinaisons. "
                "Garantit un gain minimum si vos numéros sont tirés."
            ),
        )

    async def get_user_plans(
        self, user_id: int, game_id: int, *, limit: int = 50
    ) -> list[BudgetPlan]:
        return await self._repo.get_by_user_and_game(user_id, game_id, limit=limit)

    async def get_plan(self, plan_id: int) -> BudgetPlan | None:
        return await self._repo.get(plan_id)

    async def delete_plan(self, plan_id: int, user_id: int) -> bool:
        plan = await self._repo.get(plan_id)
        if plan is None or plan.user_id != user_id:
            return False
        await self._repo.delete(plan)
        return True
