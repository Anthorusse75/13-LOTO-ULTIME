import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

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


async def _seed_games() -> None:
    """Upsert game_definitions from YAML configs — adds new games without touching existing ones."""
    from app.core.game_definitions import load_all_game_configs
    from app.models.base import get_session
    from app.models.game import GameDefinition
    from app.repositories.game_repository import GameRepository

    logger = structlog.get_logger("seed")

    async for session in get_session():
        repo = GameRepository(session)
        configs = load_all_game_configs()
        added: list[str] = []
        for cfg in configs.values():
            existing = await repo.get_by_slug(cfg.slug)
            if existing:
                continue  # already in DB — don't overwrite
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
            added.append(cfg.slug)

        if added:
            await session.commit()
            logger.info("seed_games.done", added=added)
        else:
            logger.info("seed_games.all_present", count=len(configs))
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


async def _maybe_initial_fetch() -> None:
    """If no draws exist yet, trigger the nightly pipeline in the background."""
    import asyncio

    from sqlalchemy import func, select

    from app.models.base import get_session
    from app.models.draw import Draw

    logger = structlog.get_logger("seed")

    async for session in get_session():
        result = await session.execute(select(func.count(Draw.id)))
        count = result.scalar()
        break

    if count and count > 0:
        logger.info("initial_fetch.skipped", draw_count=count)
        return

    logger.info("initial_fetch.starting", reason="empty_draws_table")

    async def _run_pipeline() -> None:
        try:
            from app.scheduler.jobs.nightly_pipeline import _do_nightly_pipeline

            result = await _do_nightly_pipeline()
            logger.info("initial_fetch.complete", result=result)
        except Exception as exc:
            logger.error("initial_fetch.failed", error=str(exc))

    asyncio.create_task(_run_pipeline())


async def _maybe_initial_compute() -> None:
    """If compute jobs have never run successfully, trigger them in the background.

    Checks each computation step independently so that only the missing ones
    are executed (e.g. draws already fetched but stats never computed).
    """
    import asyncio

    from sqlalchemy import select

    from app.models.base import get_session
    from app.models.job import JobExecution, JobStatus

    logger = structlog.get_logger("seed")

    # Jobs to check, in execution order (each depends on the previous)
    compute_jobs = [
        "compute_stats",
        "compute_scoring",
        "compute_top_grids",
        "optimize_portfolio",
    ]

    never_ran: list[str] = []
    async for session in get_session():
        for job_name in compute_jobs:
            # Skip if already succeeded OR currently running
            stmt = (
                select(JobExecution.id)
                .where(
                    JobExecution.job_name == job_name,
                    JobExecution.status.in_([JobStatus.SUCCESS, JobStatus.RUNNING]),
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            if result.scalar() is None:
                never_ran.append(job_name)
        break

    if not never_ran:
        logger.info("initial_compute.skipped", reason="all_jobs_already_ran")
        return

    # If an early step never ran, all subsequent steps must also run
    first_missing_idx = compute_jobs.index(never_ran[0])
    jobs_to_run = compute_jobs[first_missing_idx:]
    logger.info("initial_compute.starting", jobs=jobs_to_run)

    async def _run_compute() -> None:
        from app.scheduler.jobs.compute_scoring import _do_compute_scoring
        from app.scheduler.jobs.compute_statistics import _do_compute_stats
        from app.scheduler.jobs.compute_top_grids import _do_compute_top_grids
        from app.scheduler.jobs.optimize_portfolio import _do_optimize_portfolio
        from app.scheduler.runner import execute_with_tracking

        job_funcs: dict[str, Any] = {
            "compute_stats": _do_compute_stats,
            "compute_scoring": _do_compute_scoring,
            "compute_top_grids": _do_compute_top_grids,
            "optimize_portfolio": _do_optimize_portfolio,
        }

        for job_name in jobs_to_run:
            try:
                await execute_with_tracking(
                    job_name=job_name,
                    func=job_funcs[job_name],
                    triggered_by="startup",
                )
                logger.info("initial_compute.step_done", job=job_name)
            except Exception as exc:
                logger.error("initial_compute.step_failed", job=job_name, error=str(exc))
                # Continue to next step even if one fails

    asyncio.create_task(_run_compute())


async def _cleanup_stale_jobs() -> None:
    """Mark any RUNNING jobs from a previous process as FAILED on startup."""
    from datetime import UTC, datetime

    from sqlalchemy import update

    from app.models.base import get_session
    from app.models.job import JobExecution, JobStatus

    logger = structlog.get_logger("seed")

    async for session in get_session():
        stmt = (
            update(JobExecution)
            .where(JobExecution.status == JobStatus.RUNNING)
            .values(
                status=JobStatus.FAILED,
                error_message="Marked stale: server restarted while job was running",
                finished_at=datetime.now(UTC),
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount:  # type: ignore[union-attr]
            logger.warning("stale_jobs_cleaned", count=result.rowcount)
        break


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown logic."""
    setup_logging(log_level=settings.LOG_LEVEL, json_output=settings.LOG_JSON)
    init_db(settings.DATABASE_URL)
    logger = structlog.get_logger("app")
    logger.info("application_started", version=settings.APP_VERSION)

    # Clean up stale RUNNING jobs from previous crashes
    await _cleanup_stale_jobs()

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

    # On first deployment, trigger data fetch in the background
    await _maybe_initial_fetch()

    # If draws exist but compute jobs never ran, trigger them
    await _maybe_initial_compute()

    yield

    # Shutdown scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=True)
        logger.info("scheduler_stopped")

    await close_db()
    logger.info("application_stopped")


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = exc.detail.split(" ")[-1] if exc.detail else "60"
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMIT_EXCEEDED",
            "detail": "Trop de requêtes — réessayez plus tard",
            "retry_after": retry_after,
        },
        headers={"Retry-After": retry_after},
    )


def create_app() -> FastAPI:
    """Factory de l'application FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # ── Rate Limiting ──
    from app.core.rate_limit import limiter

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
    async def timing_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        import time as _time

        from app.core.metrics import http_request_duration_seconds, http_requests_total

        start = _time.perf_counter()
        response: Response = await call_next(request)
        duration = _time.perf_counter() - start
        duration_ms = duration * 1000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        # Record Prometheus metrics (skip /metrics endpoint itself)
        path = request.url.path
        if path != "/metrics":
            # Normalize dynamic path segments to avoid label cardinality explosion
            # e.g. /api/v1/games/123/draws → /api/v1/games/{id}/draws
            import re

            norm_path = re.sub(r"/\d+", "/{id}", path)
            method = request.method
            status = str(response.status_code)
            http_requests_total.labels(method=method, endpoint=norm_path, status_code=status).inc()
            http_request_duration_seconds.labels(method=method, endpoint=norm_path).observe(
                duration
            )

        return response

    @app.middleware("http")
    async def logging_context_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def security_headers_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # HSTS — only in production (requires HTTPS)
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response

    # ── Exception handlers ──
    @app.exception_handler(GameNotFoundError)
    async def game_not_found_handler(request: Request, exc: GameNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DrawAlreadyExistsError)
    async def draw_exists_handler(request: Request, exc: DrawAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidDrawDataError)
    async def invalid_draw_handler(request: Request, exc: InvalidDrawDataError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InsufficientDataError)
    async def insufficient_data_handler(
        request: Request, exc: InsufficientDataError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def authz_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    # ── Health check ──
    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, Any]:
        import shutil
        from datetime import UTC, datetime

        from sqlalchemy import func, select, text

        from app.models.base import get_session
        from app.models.draw import Draw
        from app.models.grid import ScoredGrid
        from app.models.job import JobExecution
        from app.models.statistics import StatisticsSnapshot

        # ── Database ──
        db_status = "ok"
        db_latency_ms: float | None = None
        draw_count = 0
        grid_count = 0
        last_draw_date: str | None = None
        last_stats_date: str | None = None
        last_job_status: str | None = None
        last_job_name: str | None = None
        last_job_date: str | None = None

        try:
            t0 = time.perf_counter()
            async for session in get_session():
                # Connectivity ping
                await session.execute(text("SELECT 1"))
                db_latency_ms = round((time.perf_counter() - t0) * 1000, 2)

                result = await session.execute(select(func.count(Draw.id)))
                draw_count = result.scalar() or 0

                result = await session.execute(select(func.count(ScoredGrid.id)))
                grid_count = result.scalar() or 0

                # Latest draw date across all games
                result = await session.execute(select(func.max(Draw.draw_date)))
                latest_draw = result.scalar()
                if latest_draw:
                    last_draw_date = str(latest_draw)

                # Latest stats snapshot
                result = await session.execute(select(func.max(StatisticsSnapshot.computed_at)))
                latest_stats = result.scalar()
                if latest_stats:
                    last_stats_date = str(latest_stats)

                # Latest job execution
                job_result = await session.execute(
                    select(JobExecution).order_by(JobExecution.started_at.desc()).limit(1)
                )
                last_job = job_result.scalars().first()
                if last_job:
                    last_job_status = last_job.status
                    last_job_name = last_job.job_name
                    last_job_date = str(last_job.started_at)

                break
        except Exception as exc:
            db_status = f"error: {type(exc).__name__}"

        # ── Scheduler ──
        scheduler_status = "disabled"
        scheduler_jobs: list[str] = []
        if settings.SCHEDULER_ENABLED:
            try:
                from app.scheduler import get_scheduler

                sched = get_scheduler()
                if sched is not None and sched.running:
                    scheduler_status = "running"
                    scheduler_jobs = [job.id for job in sched.get_jobs()]
                else:
                    scheduler_status = "stopped"
            except Exception:
                scheduler_status = "error"

        # ── Disk ──
        disk_info: dict[str, Any] = {}
        try:
            usage = shutil.disk_usage(".")
            disk_info = {
                "total_gb": round(usage.total / 1e9, 2),
                "used_gb": round(usage.used / 1e9, 2),
                "free_gb": round(usage.free / 1e9, 2),
                "used_percent": round(usage.used / usage.total * 100, 1),
            }
        except Exception:
            disk_info = {"error": "unavailable"}

        # ── Overall status ──
        is_healthy = db_status == "ok" and disk_info.get("used_percent", 0) < 95
        overall = "healthy" if is_healthy else "degraded"

        return {
            "status": overall,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
                "draws_count": draw_count,
                "grids_count": grid_count,
                "last_draw_date": last_draw_date,
                "last_stats_computed_at": last_stats_date,
            },
            "scheduler": {
                "status": scheduler_status,
                "jobs": scheduler_jobs,
            },
            "last_job": {
                "name": last_job_name,
                "status": last_job_status,
                "started_at": last_job_date,
            },
            "disk": disk_info,
        }

    # ── Prometheus /metrics endpoint ──
    from app.core.metrics import metrics_app

    app.mount("/metrics", metrics_app)

    # ── API v1 router ──
    from app.api.v1 import api_v1_router

    app.include_router(api_v1_router)

    return app


app = create_app()
