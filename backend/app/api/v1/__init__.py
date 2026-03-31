from fastapi import APIRouter

from .auth import router as auth_router
from .database import router as database_router
from .draws import router as draws_router
from .games import router as games_router
from .grids import router as grids_router
from .health import router as health_router
from .jobs import router as jobs_router
from .portfolios import router as portfolios_router
from .simulations import router as simulations_router
from .statistics import router as statistics_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(database_router, prefix="/admin/database", tags=["Database Admin"])
api_v1_router.include_router(games_router, prefix="/games", tags=["Games"])
api_v1_router.include_router(health_router, prefix="/system", tags=["System"])
api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_v1_router.include_router(
    draws_router,
    prefix="/games/{game_id}/draws",
    tags=["Draws"],
)
api_v1_router.include_router(
    statistics_router,
    prefix="/games/{game_id}/statistics",
    tags=["Statistics"],
)
api_v1_router.include_router(
    grids_router,
    prefix="/games/{game_id}/grids",
    tags=["Grids"],
)
api_v1_router.include_router(
    portfolios_router,
    prefix="/games/{game_id}/portfolios",
    tags=["Portfolios"],
)
api_v1_router.include_router(
    simulations_router,
    prefix="/games/{game_id}/simulation",
    tags=["Simulation"],
)
