from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ScoreBreakdown(BaseModel):
    frequency: float
    gap: float
    cooccurrence: float
    structure: float
    balance: float
    pattern_penalty: float


class GridScoreRequest(BaseModel):
    numbers: list[int] = Field(..., min_length=1, max_length=10)
    stars: list[int] | None = None
    profile: str = Field("equilibre", pattern=r"^(equilibre|tendance|contrarian|structurel)$")
    weights: dict[str, float] | None = None

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Les numéros doivent être uniques")
        for n in v:
            if n < 1:
                raise ValueError("Les numéros doivent être >= 1")
        return sorted(v)

    @field_validator("stars")
    @classmethod
    def validate_stars(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return v
        if len(v) != len(set(v)):
            raise ValueError("Les étoiles doivent être uniques")
        for s in v:
            if s < 1:
                raise ValueError("Les étoiles doivent être >= 1")
        return sorted(v)


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
    is_favorite: bool = False
    is_played: bool = False
    played_at: datetime | None = None

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
