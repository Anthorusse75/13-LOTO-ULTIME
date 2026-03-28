"""Job execution runner with retry, logging, and historisation."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog

from app.models.base import get_session
from app.models.job import JobExecution, JobStatus
from app.repositories.job_repository import JobRepository

logger = structlog.get_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAYS = [0, 5, 30]  # seconds: immediate, 5s, 30s


async def execute_with_tracking(
    job_name: str,
    func,
    *args: Any,
    game_id: int | None = None,
    triggered_by: str = "scheduler",
    **kwargs: Any,
) -> JobExecution:
    """Execute a job function with full tracking, retry, and historisation."""
    log = logger.bind(job_name=job_name, triggered_by=triggered_by)

    job_execution = JobExecution(
        job_name=job_name,
        game_id=game_id,
        status=JobStatus.RUNNING,
        started_at=datetime.now(UTC),
        triggered_by=triggered_by,
    )

    # Persist the RUNNING state
    async for session in get_session():
        repo = JobRepository(session)
        job_execution = await repo.create(job_execution)
        await session.commit()
        break

    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            log.info("job_attempt_start", attempt=attempt + 1)
            result_summary = await func(*args, **kwargs)

            job_execution.status = JobStatus.SUCCESS
            job_execution.result_summary = result_summary or {}
            log.info("job_succeeded", attempt=attempt + 1)
            break

        except Exception as exc:
            last_error = exc
            log.warning(
                "job_attempt_failed",
                attempt=attempt + 1,
                error=str(exc),
            )
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                if delay > 0:
                    log.info("job_retry_waiting", delay_seconds=delay)
                    await asyncio.sleep(delay)
            else:
                job_execution.status = JobStatus.FAILED
                job_execution.error_message = str(exc)
                log.error("job_max_retries_exceeded", error=str(exc))

    job_execution.finished_at = datetime.now(UTC)
    started = job_execution.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    job_execution.duration_seconds = (
        job_execution.finished_at - started
    ).total_seconds()

    # Persist final state
    async for session in get_session():
        merged = await session.merge(job_execution)
        await session.commit()
        return merged

    return job_execution
