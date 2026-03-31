"""History endpoints — /api/v1/history."""

import math
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.dependencies import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.repositories.saved_result_repository import SavedResultRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.history import SaveResultRequest, SavedResultResponse, UpdateTagsRequest
from app.services.history import HistoryService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


def _get_history_service(
    session: AsyncSession = Depends(get_db),
) -> HistoryService:
    return HistoryService(SavedResultRepository(session))


@router.post("/save", response_model=SavedResultResponse, status_code=201)
async def save_result(
    body: SaveResultRequest,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """Save a computation result to user history."""
    result = await service.save_result(
        user_id=current_user.id,
        result_type=body.result_type,
        parameters=body.parameters,
        result_data=body.result_data,
        game_id=body.game_id,
        name=body.name,
        tags=body.tags,
    )
    return result


@router.get("", response_model=PaginatedResponse[SavedResultResponse])
async def list_results(
    pagination: PaginationParams = Depends(),
    result_type: str | None = None,
    is_favorite: bool | None = None,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """List saved results for the current user (paginated, filterable)."""
    data = await service.list_results(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        result_type=result_type,
        is_favorite=is_favorite,
    )
    return PaginatedResponse(
        items=data["items"],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        pages=data["pages"],
    )


@router.get("/{result_id}", response_model=SavedResultResponse)
async def get_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """Get a single saved result by ID (ownership check)."""
    result = await service.get_result(result_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Résultat non trouvé")
    return result


@router.delete("/{result_id}", status_code=204)
async def delete_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> None:
    """Delete a saved result (ownership check)."""
    deleted = await service.delete_result(result_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Résultat non trouvé")


@router.patch("/{result_id}/favorite", response_model=dict)
async def toggle_favorite(
    result_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """Toggle favorite status on a saved result."""
    new_value = await service.toggle_favorite(result_id, current_user.id)
    if new_value is None:
        raise HTTPException(status_code=404, detail="Résultat non trouvé")
    return {"is_favorite": new_value}


@router.patch("/{result_id}/tags", response_model=dict)
async def update_tags(
    result_id: int,
    body: UpdateTagsRequest,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """Update tags on a saved result."""
    updated = await service.update_tags(result_id, current_user.id, body.tags)
    if not updated:
        raise HTTPException(status_code=404, detail="Résultat non trouvé")
    return {"tags": body.tags}


@router.post("/{result_id}/duplicate", response_model=SavedResultResponse, status_code=201)
async def duplicate_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(_get_history_service),
) -> Any:
    """Duplicate a saved result."""
    copy = await service.duplicate_result(result_id, current_user.id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Résultat non trouvé")
    return copy
