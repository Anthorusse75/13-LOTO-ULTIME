from fastapi import APIRouter

from .games import router as games_router
from .health import router as health_router
from .statistics import router as statistics_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(games_router, prefix="/games", tags=["Games"])
api_v1_router.include_router(health_router, prefix="/system", tags=["System"])
api_v1_router.include_router(
    statistics_router,
    prefix="/games/{game_id}/statistics",
    tags=["Statistics"],
)
