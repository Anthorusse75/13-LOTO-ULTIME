import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DrawAlreadyExistsError,
    GameNotFoundError,
    InsufficientDataError,
    InvalidDrawDataError,
)
from app.core.logging import setup_logging
from app.models.base import close_db, init_db

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


async def _seed_games() -> None:
    """Seed game_definitions from YAML configs if the table is empty."""
    from app.core.game_definitions import load_all_game_configs
    from app.models.base import get_session
    from app.models.game import GameDefinition
    from app.repositories.game_repository import GameRepository

    logger = structlog.get_logger("seed")

    async for session in get_session():
        repo = GameRepository(session)
        existing = await repo.get_active_games()
        if existing:
            logger.info("seed_games.skipped", count=len(existing))
            break

        configs = load_all_game_configs()
        for cfg in configs.values():
            game = GameDefinition(
                name=cfg.name,
                slug=cfg.slug,
                numbers_pool=cfg.numbers_pool,
                numbers_drawn=cfg.numbers_drawn,
                min_number=cfg.min_number,
                max_number=cfg.max_number,
                stars_pool=cfg.stars_pool,
                stars_drawn=cfg.stars_drawn,
                star_name=cfg.star_name,
                draw_frequency=cfg.draw_frequency,
                historical_source=cfg.historical_source,
                description=cfg.description,
                is_active=True,
            )
            session.add(game)

        await session.commit()
        logger.info("seed_games.done", games=[c.slug for c in configs.values()])
        break


async def _seed_admin() -> None:
    """Seed the initial admin user if no users exist."""
    from app.models.base import get_session
    from app.repositories.user_repository import UserRepository
    from app.services.auth import create_initial_admin

    async for session in get_session():
        repo = UserRepository(session)
        await create_initial_admin(repo, settings)
        await session.commit()
        break


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic."""
    setup_logging(log_level=settings.LOG_LEVEL, json_output=settings.LOG_JSON)
    init_db(settings.DATABASE_URL)
    logger = structlog.get_logger("app")
    logger.info("application_started", version=settings.APP_VERSION)

    # Seed games from YAML if table is empty
    await _seed_games()

    # Seed initial admin user if no users exist
    await _seed_admin()

    # Start scheduler if enabled
    scheduler = None
    if settings.SCHEDULER_ENABLED:
        from app.scheduler import create_scheduler

        scheduler = create_scheduler(settings)
        scheduler.start()
        logger.info("scheduler_started")

    yield

    # Shutdown scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")

    await close_db()
    logger.info("application_stopped")


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de requêtes — réessayez plus tard"},
    )


def create_app() -> FastAPI:
    """Factory de l'application FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # ── Rate Limiting ──
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)  # type: ignore[arg-type]

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middlewares ──
    @app.middleware("http")
    async def timing_middleware(request: Request, call_next):
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response

    @app.middleware("http")
    async def logging_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # ── Exception handlers ──
    @app.exception_handler(GameNotFoundError)
    async def game_not_found_handler(request: Request, exc: GameNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DrawAlreadyExistsError)
    async def draw_exists_handler(request: Request, exc: DrawAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidDrawDataError)
    async def invalid_draw_handler(request: Request, exc: InvalidDrawDataError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InsufficientDataError)
    async def insufficient_data_handler(request: Request, exc: InsufficientDataError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def authz_error_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    # ── Health check ──
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}

    # ── API v1 router ──
    from app.api.v1 import api_v1_router

    app.include_router(api_v1_router)

    return app


app = create_app()
