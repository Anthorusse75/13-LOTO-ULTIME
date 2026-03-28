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
    from app.scheduler.jobs.compute_scoring import compute_scoring_job
    from app.scheduler.jobs.compute_statistics import compute_stats_job
    from app.scheduler.jobs.compute_top_grids import compute_top_grids_job
    from app.scheduler.jobs.fetch_draws import fetch_draws_job
    from app.scheduler.jobs.health_check import health_check_job
    from app.scheduler.jobs.optimize_portfolio import optimize_portfolio_job

    # Loto FDJ : lundi, mercredi, samedi à 22h
    scheduler.add_job(
        fetch_draws_job,
        "cron",
        id="fetch_loto",
        day_of_week="mon,wed,sat",
        hour=22,
        minute=0,
        args=["loto-fdj"],
        replace_existing=True,
    )

    # EuroMillions : mardi, vendredi à 22h
    scheduler.add_job(
        fetch_draws_job,
        "cron",
        id="fetch_euromillions",
        day_of_week="tue,fri",
        hour=22,
        minute=0,
        args=["euromillions"],
        replace_existing=True,
    )

    # Recalcul statistiques : tous les jours à 23h
    scheduler.add_job(
        compute_stats_job,
        "cron",
        id="compute_stats",
        hour=23,
        minute=0,
        replace_existing=True,
    )

    # Recalcul scoring : tous les jours à 23h30
    scheduler.add_job(
        compute_scoring_job,
        "cron",
        id="compute_scoring",
        hour=23,
        minute=30,
        replace_existing=True,
    )

    # Top grilles : tous les jours à 23h45
    scheduler.add_job(
        compute_top_grids_job,
        "cron",
        id="compute_top_grids",
        hour=23,
        minute=45,
        replace_existing=True,
    )

    # Optimisation portefeuille : quotidien 0h00
    scheduler.add_job(
        optimize_portfolio_job,
        "cron",
        id="optimize_portfolio",
        hour=0,
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
