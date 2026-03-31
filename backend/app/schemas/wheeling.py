"""Wheeling system Pydantic schemas — request / response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── Request schemas ──


class WheelingPreviewRequest(BaseModel):
    numbers: list[int] = Field(..., min_length=6, max_length=20)
    stars: list[int] | None = Field(None, max_length=6)
    guarantee: int = Field(3, ge=2)


class WheelingGenerateRequest(BaseModel):
    numbers: list[int] = Field(..., min_length=6, max_length=20)
    stars: list[int] | None = Field(None, max_length=6)
    guarantee: int = Field(3, ge=2)


# ── Response schemas ──


class WheelingGridItem(BaseModel):
    numbers: list[int]
    stars: list[int] | None = None


class GainScenarioSchema(BaseModel):
    rank: int
    name: str
    match_numbers: int
    match_stars: int
    avg_prize: float
    matching_grids_best: int
    matching_grids_avg: float
    matching_grids_worst: int
    potential_gain_best: float
    potential_gain_avg: float
    potential_gain_worst: float


class WheelingPreviewResponse(BaseModel):
    estimated_grid_count: int
    estimated_cost: float
    total_t_combinations: int
    full_wheel_size: int
    reduction_rate_estimate: float


class WheelingGenerateResponse(BaseModel):
    id: int | None = None
    grids: list[WheelingGridItem]
    grid_count: int
    total_cost: float
    coverage_rate: float
    reduction_rate: float
    total_t_combinations: int
    full_wheel_size: int
    computation_time_ms: float
    gain_scenarios: list[GainScenarioSchema] = []
    number_distribution: dict[int, int] = {}


class WheelingSystemResponse(BaseModel):
    id: int
    game_id: int
    selected_numbers: list[int]
    selected_stars: list[int] | None
    guarantee_level: int
    grids: list[WheelingGridItem]
    grid_count: int
    total_cost: float
    coverage_rate: float
    reduction_rate: float
    created_at: datetime

    model_config = {"from_attributes": True}
