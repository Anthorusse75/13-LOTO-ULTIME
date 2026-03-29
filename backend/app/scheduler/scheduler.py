"""Scheduler setup — APScheduler AsyncIOScheduler configuration."""

from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings

logger = structlog.get_logger(__name__)

# Module-level reference so health check can inspect the running scheduler
_scheduler_instance: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler | None:
    """Return the running scheduler instance (or None if not started)."""
    return _scheduler_instance


def create_scheduler(settings: Settings) -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    global _scheduler_instance

    job_defaults = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 3600,
    }

    scheduler = AsyncIOScheduler(
        job_defaults=job_defaults,
        timezone="Europe/Paris",
    )

    _register_jobs(scheduler)
    _scheduler_instance = scheduler

    logger.info("scheduler_configured", job_count=len(scheduler.get_jobs()))
    return scheduler


def _register_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register all scheduled jobs."""
    from app.scheduler.jobs.backup_db import backup_db_job
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

    # Backup DB : hebdomadaire dimanche 4h
    scheduler.add_job(
        backup_db_job,
        "cron",
        id="backup_db",
        day_of_week="sun",
        hour=4,
        minute=0,
        replace_existing=True,
    )
