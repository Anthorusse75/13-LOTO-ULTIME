from pydantic import BaseModel, Field


class GameDefinitionResponse(BaseModel):
    id: int
    name: str
    slug: str
    numbers_pool: int
    numbers_drawn: int
    min_number: int
    max_number: int
    stars_pool: int | None
    stars_drawn: int | None
    star_name: str | None
    draw_frequency: str
    is_active: bool

    model_config = {"from_attributes": True}


class GameDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    numbers_pool: int = Field(..., ge=5, le=100)
    numbers_drawn: int = Field(..., ge=1, le=20)
    min_number: int = Field(1, ge=0)
    max_number: int = Field(..., ge=5, le=100)
    stars_pool: int | None = Field(None, ge=1, le=50)
    stars_drawn: int | None = Field(None, ge=1, le=10)
    star_name: str | None = None
    draw_frequency: str = ""
    historical_source: str = ""
    description: str | None = None
