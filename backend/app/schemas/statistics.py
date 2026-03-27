from datetime import datetime

from pydantic import BaseModel


class FrequencyItem(BaseModel):
    number: int
    count: int
    relative_frequency: float
    last_seen: int


class GapItem(BaseModel):
    number: int
    current_gap: int
    max_gap: int
    avg_gap: float
    min_gap: int


class CooccurrenceItem(BaseModel):
    pair: tuple[int, int]
    count: int
    expected: float
    affinity: float


class StatisticsResponse(BaseModel):
    game_id: int
    computed_at: datetime
    draw_count: int
    frequencies: list[FrequencyItem]
    gaps: list[GapItem]
    top_cooccurrences: list[CooccurrenceItem]
    hot_numbers: list[int]
    cold_numbers: list[int]
    distribution_entropy: float
    uniformity_score: float
