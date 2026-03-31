"""Schemas for daily suggestions."""

from __future__ import annotations

from pydantic import BaseModel


class SuggestionGrid(BaseModel):
    numbers: list[int]
    stars: list[int] | None = None
    total_score: float
    method: str


class DailySuggestionResponse(BaseModel):
    game_id: int
    date: str
    grids: list[SuggestionGrid]
    reason: str
