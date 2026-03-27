from datetime import datetime

from pydantic import BaseModel, Field


class PortfolioGridItem(BaseModel):
    numbers: list[int]
    stars: list[int] | None
    score: float


class PortfolioResponse(BaseModel):
    id: int
    game_id: int
    name: str
    strategy: str
    grid_count: int
    grids: list[PortfolioGridItem]
    diversity_score: float
    coverage_score: float
    avg_grid_score: float
    min_hamming_distance: float | None
    computed_at: datetime

    model_config = {"from_attributes": True}


class PortfolioGenerateRequest(BaseModel):
    grid_count: int = Field(10, ge=2, le=50)
    strategy: str = Field(
        "balanced",
        pattern=r"^(max_diversity|max_coverage|balanced|min_correlation)$",
    )
