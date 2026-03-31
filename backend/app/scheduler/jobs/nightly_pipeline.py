"""Job: nightly pipeline orchestrator — chains all steps sequentially."""

from collections.abc import Callable, Coroutine
from typing import Any

import structlog

from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def nightly_pipeline_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: run the full nightly pipeline in order."""
    await execute_with_tracking(
        job_name="nightly_pipeline",
        func=_do_nightly_pipeline,
        triggered_by=triggered_by,
    )


async def _do_nightly_pipeline() -> dict[str, Any]:
    """Core logic — chain fetch → stats → scoring → top grids → portfolio."""
    from app.scheduler.jobs.check_played_grids import _do_check_played_grids
    from app.scheduler.jobs.cleanup_notifications import _do_cleanup_notifications
    from app.scheduler.jobs.compute_hot_cold import _do_compute_hot_cold
    from app.scheduler.jobs.compute_scoring import _do_compute_scoring
    from app.scheduler.jobs.compute_statistics import _do_compute_stats
    from app.scheduler.jobs.compute_top_grids import _do_compute_top_grids
    from app.scheduler.jobs.create_notifications import _do_create_grid_result_notifications
    from app.scheduler.jobs.fetch_draws import _do_fetch
    from app.scheduler.jobs.optimize_portfolio import _do_optimize_portfolio
    from app.scheduler.jobs.pre_generate_daily_content import _do_pre_generate

    results: dict[str, Any] = {}
    steps: list[tuple[str, Callable[..., Coroutine[Any, Any, dict[str, Any]]]]] = [
        ("fetch_loto", lambda: _do_fetch("loto-fdj")),
        ("fetch_euromillions", lambda: _do_fetch("euromillions")),
        ("fetch_keno", lambda: _do_fetch("keno")),
        ("compute_stats", _do_compute_stats),
        ("compute_scoring", _do_compute_scoring),
        ("compute_top_grids", _do_compute_top_grids),
        ("optimize_portfolio", _do_optimize_portfolio),
        ("compute_hot_cold", _do_compute_hot_cold),
        ("pre_generate_daily_content", _do_pre_generate),
        ("check_played_grids", _do_check_played_grids),
        ("create_grid_result_notifications", _do_create_grid_result_notifications),
        ("cleanup_notifications", _do_cleanup_notifications),
    ]

    for step_name, step_func in steps:
        try:
            step_result = await step_func()
            results[step_name] = {"status": "success", "detail": step_result}
            logger.info("nightly_pipeline.step_done", step=step_name)
        except Exception as exc:
            results[step_name] = {"status": "error", "error": str(exc)}
            logger.error("nightly_pipeline.step_failed", step=step_name, error=str(exc))
            # Continue to next step even if one fails

    return {"steps": len(results), "details": results}
