"""Scheduler setup — APScheduler AsyncIOScheduler configuration."""

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings

logger = structlog.get_logger(__name__)


def create_scheduler(settings: Settings) -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    job_defaults = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 3600,
    }

    scheduler = AsyncIOScheduler(job_defaults=job_defaults)

    _register_jobs(scheduler)

    logger.info("scheduler_configured", job_count=len(scheduler.get_jobs()))
    return scheduler


def _register_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register all scheduled jobs."""
    from app.scheduler.jobs.cleanup import cleanup_job
    from app.scheduler.jobs.health_check import health_check_job
    from app.scheduler.jobs.nightly_pipeline import nightly_pipeline_job

    # Nightly pipeline : tous les jours à 22h — orchestre fetch→stats→scoring→top→portfolio
    scheduler.add_job(
        nightly_pipeline_job,
        "cron",
        id="nightly_pipeline",
        hour=22,
        minute=0,
        replace_existing=True,
    )

    # Nettoyage : quotidien 3h
    scheduler.add_job(
        cleanup_job,
        "cron",
        id="cleanup",
        hour=3,
        minute=0,
        replace_existing=True,
    )

    # Health check : toutes les 30 minutes
    scheduler.add_job(
        health_check_job,
        "interval",
        id="health_check",
        minutes=30,
        replace_existing=True,
    )
