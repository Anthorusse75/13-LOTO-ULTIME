from datetime import datetime

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    frequency: float
    gap: float
    cooccurrence: float
    structure: float
    balance: float
    pattern_penalty: float


class GridScoreRequest(BaseModel):
    numbers: list[int] = Field(..., min_length=1)
    stars: list[int] | None = None
    profile: str = Field("equilibre", pattern=r"^(equilibre|tendance|contrarian|structurel)$")
    weights: dict[str, float] | None = None


class GridScoreResponse(BaseModel):
    numbers: list[int]
    stars: list[int] | None = None
    total_score: float
    score_breakdown: ScoreBreakdown
    star_score: float | None = None


class GridResponse(BaseModel):
    id: int
    numbers: list[int]
    stars: list[int] | None
    total_score: float
    score_breakdown: ScoreBreakdown
    rank: int | None
    method: str
    computed_at: datetime

    model_config = {"from_attributes": True}


class GridGenerateRequest(BaseModel):
    count: int = Field(10, ge=1, le=100)
    method: str = Field("auto", pattern=r"^(auto|genetic|annealing|tabu|hill_climbing)$")
    profile: str = Field("equilibre", pattern=r"^(equilibre|tendance|contrarian|structurel)$")
    weights: dict[str, float] | None = None


class GridGenerateResponse(BaseModel):
    grids: list["GridScoreResponse"]
    computation_time_ms: float
    method_used: str
