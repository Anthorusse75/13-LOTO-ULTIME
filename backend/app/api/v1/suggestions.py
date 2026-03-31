"""Suggestions API — daily grid suggestions."""

from fastapi import APIRouter, Depends, Path, Query

from app.dependencies import (
    get_current_user,
    get_suggestion_service,
    require_role,
)
from app.models.user import User, UserRole
from app.schemas.suggestion import DailySuggestionResponse
from app.services.suggestion import SuggestionService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.get("/daily", response_model=DailySuggestionResponse)
async def get_daily_suggestions(
    game_id: int = Path(..., gt=0),
    count: int = Query(3, ge=1, le=10),
    service: SuggestionService = Depends(get_suggestion_service),
    user: User = Depends(get_current_user),
) -> DailySuggestionResponse:
    """Get daily grid suggestions for a game."""
    return await service.get_daily_suggestion(game_id, count=count)
