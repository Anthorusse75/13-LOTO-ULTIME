"""Jobs API — manual trigger and history endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_job_repository
from app.models.job import JobExecution, JobStatus
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobExecutionResponse

router = APIRouter()

# Allowed jobs for manual triggering
TRIGGERABLE_JOBS = {
    "fetch_loto": ("fetch_draws", ["loto-fdj"]),
    "fetch_euromillions": ("fetch_draws", ["euromillions"]),
    "compute_stats": ("compute_statistics", []),
    "compute_scoring": ("compute_scoring", []),
    "compute_top_grids": ("compute_top_grids", []),
    "optimize_portfolio": ("optimize_portfolio", []),
    "cleanup": ("cleanup", []),
    "health_check": ("health_check", []),
}


@router.post("/{job_name}/trigger", response_model=JobExecutionResponse)
async def trigger_job(
    job_name: str,
    job_repo: JobRepository = Depends(get_job_repository),
):
    """Manually trigger a scheduled job."""
    if job_name not in TRIGGERABLE_JOBS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown job '{job_name}'. Available: {list(TRIGGERABLE_JOBS.keys())}",
        )

    # Check no instance is already running
    running = await job_repo.get_running_jobs()
    running_names = {j.job_name for j in running}
    module_name, args = TRIGGERABLE_JOBS[job_name]

    # Match on prefix for fetch jobs (e.g. fetch_draws_loto-fdj)
    for rn in running_names:
        if rn.startswith(module_name):
            raise HTTPException(
                status_code=409,
                detail=f"Job '{job_name}' is already running.",
            )

    # Import and launch the job function in background
    import asyncio

    job_func = _resolve_job_func(module_name)

    async def _run_job():
        """Wrapper to catch and log exceptions from fire-and-forget tasks."""
        try:
            await job_func(*args, triggered_by="manual")
        except Exception:
            import structlog

            structlog.get_logger("jobs").exception("trigger_job.background_error", job=job_name)

    task = asyncio.create_task(_run_job())
    # We don't await — return immediately with a PENDING status indicator

    # Return the latest execution record (will be RUNNING once the task starts)
    # Give a small moment for the task to create its record
    await asyncio.sleep(0.1)

    latest = await job_repo.get_latest_by_name(f"{module_name}_{args[0]}" if args else module_name)
    if latest is None:
        # Job hasn't created its record yet — return a synthetic response
        from datetime import UTC, datetime

        return JobExecutionResponse(
            id=0,
            job_name=job_name,
            game_id=None,
            status=JobStatus.PENDING,
            started_at=datetime.now(UTC),
            finished_at=None,
            duration_seconds=None,
            result_summary=None,
            error_message=None,
            triggered_by="manual",
        )

    return latest


@router.get("/", response_model=list[JobExecutionResponse])
async def list_job_executions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List recent job executions (paginated)."""
    stmt = select(JobExecution).order_by(JobExecution.started_at.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{job_name}/history", response_model=list[JobExecutionResponse])
async def get_job_history(
    job_name: str,
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get execution history for a specific job."""
    stmt = (
        select(JobExecution)
        .where(JobExecution.job_name.contains(job_name))
        .order_by(JobExecution.started_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    if not rows:
        raise HTTPException(status_code=404, detail=f"No history for job '{job_name}'.")
    return rows


@router.get("/status", response_model=dict)
async def get_scheduler_status(
    job_repo: JobRepository = Depends(get_job_repository),
):
    """Get current scheduler status summary."""
    running = await job_repo.get_running_jobs()

    # Get last execution per job type
    last_runs: dict[str, dict] = {}
    for jn in TRIGGERABLE_JOBS:
        module_name, args = TRIGGERABLE_JOBS[jn]
        full_name = f"{module_name}_{args[0]}" if args else module_name
        latest = await job_repo.get_latest_by_name(full_name)
        if latest:
            last_runs[jn] = {
                "status": latest.status.value,
                "started_at": latest.started_at.isoformat(),
                "finished_at": latest.finished_at.isoformat() if latest.finished_at else None,
                "duration_seconds": latest.duration_seconds,
            }

    return {
        "running_jobs": [j.job_name for j in running],
        "running_count": len(running),
        "last_runs": last_runs,
    }


def _resolve_job_func(module_name: str):
    """Dynamically import a job function by module name."""
    job_map = {
        "fetch_draws": "app.scheduler.jobs.fetch_draws:fetch_draws_job",
        "compute_statistics": "app.scheduler.jobs.compute_statistics:compute_stats_job",
        "compute_scoring": "app.scheduler.jobs.compute_scoring:compute_scoring_job",
        "compute_top_grids": "app.scheduler.jobs.compute_top_grids:compute_top_grids_job",
        "optimize_portfolio": "app.scheduler.jobs.optimize_portfolio:optimize_portfolio_job",
        "cleanup": "app.scheduler.jobs.cleanup:cleanup_job",
        "health_check": "app.scheduler.jobs.health_check:health_check_job",
    }
    entry = job_map.get(module_name)
    if entry is None:
        raise ValueError(f"Unknown job module: {module_name}")
    module_path, func_name = entry.split(":")
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)
