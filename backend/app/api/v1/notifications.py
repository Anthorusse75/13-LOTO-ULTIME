"""Notifications API — user notification management."""

from fastapi import APIRouter, Depends, Path, Query

from app.dependencies import (
    get_current_user,
    get_notification_service,
    require_role,
)
from app.models.user import User, UserRole
from app.schemas.notification import (
    NotificationListResponse,
    NotificationOut,
    UnreadCountResponse,
)
from app.services.notification import NotificationService

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """List user notifications with pagination."""
    notifications, unread_count = await service.get_notifications(
        user.id, limit=limit, offset=offset, unread_only=unread_only
    )
    return NotificationListResponse(
        notifications=[NotificationOut.model_validate(n) for n in notifications],
        total=len(notifications),
        unread_count=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> UnreadCountResponse:
    """Get the count of unread notifications."""
    count = await service.get_unread_count(user.id)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int = Path(..., gt=0),
    service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> dict:
    """Mark a notification as read."""
    success = await service.mark_read(notification_id, user.id)
    return {"success": success}


@router.post("/read-all")
async def mark_all_read(
    service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> dict:
    """Mark all notifications as read."""
    count = await service.mark_all_read(user.id)
    return {"marked_count": count}
