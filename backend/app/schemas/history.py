"""History schemas — save/list/detail user results."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SaveResultRequest(BaseModel):
    result_type: str = Field(..., pattern=r"^(grid|portfolio|wheeling|budget_plan|comparison|simulation)$")
    parameters: dict[str, Any]
    result_data: dict[str, Any]
    game_id: int | None = None
    name: str | None = Field(None, max_length=200)
    tags: list[str] | None = None


class SavedResultResponse(BaseModel):
    id: int
    user_id: int
    game_id: int | None
    result_type: str
    name: str | None
    parameters: dict[str, Any]
    result_data: dict[str, Any]
    is_favorite: bool
    tags: list[str] | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class UpdateTagsRequest(BaseModel):
    tags: list[str] = Field(..., max_length=20)
