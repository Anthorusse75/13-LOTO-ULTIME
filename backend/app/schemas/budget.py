"""Budget plan Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BudgetOptimizeRequest(BaseModel):
    budget: float = Field(..., gt=0, le=10000)
    objective: str = Field(
        "balanced",
        pattern=r"^(coverage|quality|balanced)$",
    )
    numbers: list[int] | None = Field(None, max_length=20)


class GainScenarioSummarySchema(BaseModel):
    optimistic: float
    mean: float
    pessimistic: float


class BudgetRecommendationSchema(BaseModel):
    strategy: str
    grids: list[dict]
    grid_count: int
    total_cost: float
    avg_score: float | None
    diversity_score: float | None
    coverage_rate: float | None
    expected_gain: GainScenarioSummarySchema
    explanation: str
    is_recommended: bool


class BudgetOptimizeResponse(BaseModel):
    id: int | None = None
    budget: float
    grid_price: float
    max_grids: int
    recommendations: list[BudgetRecommendationSchema]


class BudgetPlanResponse(BaseModel):
    id: int
    game_id: int
    budget: float
    objective: str
    selected_numbers: list[int] | None
    recommendations: list[BudgetRecommendationSchema]
    chosen_strategy: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
