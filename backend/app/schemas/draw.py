from datetime import date

from pydantic import BaseModel, Field


class DrawResponse(BaseModel):
    id: int
    game_id: int
    draw_date: date
    draw_number: int | None
    numbers: list[int]
    stars: list[int] | None

    model_config = {"from_attributes": True}


class DrawCreate(BaseModel):
    draw_date: date
    draw_number: int | None = None
    numbers: list[int] = Field(..., min_length=1)
    stars: list[int] | None = None
