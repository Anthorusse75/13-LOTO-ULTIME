"""Tests for the job repository (extended methods)."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobExecution, JobStatus
from app.repositories.job_repository import JobRepository


class TestJobRepository:
    """Tests for JobRepository."""

    @pytest.fixture
    async def job_repo(self, db_session: AsyncSession) -> JobRepository:
        return JobRepository(db_session)

    @pytest.fixture
    async def sample_jobs(
        self, db_session: AsyncSession
    ) -> list[JobExecution]:
        now = datetime.utcnow()
        jobs = [
            JobExecution(
                job_name="fetch_draws_loto-fdj",
                status=JobStatus.SUCCESS,
                started_at=now - timedelta(hours=2),
                finished_at=now - timedelta(hours=1, minutes=59),
                duration_seconds=60.0,
                triggered_by="scheduler",
            ),
            JobExecution(
                job_name="fetch_draws_loto-fdj",
                status=JobStatus.RUNNING,
                started_at=now - timedelta(minutes=5),
                triggered_by="manual",
            ),
            JobExecution(
                job_name="compute_stats",
                status=JobStatus.SUCCESS,
                started_at=now - timedelta(hours=1),
                finished_at=now - timedelta(minutes=55),
                duration_seconds=300.0,
                triggered_by="scheduler",
            ),
            JobExecution(
                job_name="old_job",
                status=JobStatus.FAILED,
                started_at=now - timedelta(days=100),
                finished_at=now - timedelta(days=100),
                duration_seconds=1.0,
                error_message="old error",
                triggered_by="scheduler",
            ),
        ]
        for j in jobs:
            db_session.add(j)
        await db_session.flush()
        for j in jobs:
            await db_session.refresh(j)
        return jobs

    async def test_get_running_jobs(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution]
    ):
        running = await job_repo.get_running_jobs()
        assert len(running) == 1
        assert running[0].status == JobStatus.RUNNING
        assert running[0].job_name == "fetch_draws_loto-fdj"

    async def test_get_latest_by_name(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution]
    ):
        latest = await job_repo.get_latest_by_name("fetch_draws_loto-fdj")
        assert latest is not None
        assert latest.status == JobStatus.RUNNING  # Most recent

    async def test_get_latest_by_name_not_found(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution]
    ):
        latest = await job_repo.get_latest_by_name("nonexistent")
        assert latest is None

    async def test_get_history(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution]
    ):
        history = await job_repo.get_history("fetch_draws")
        assert len(history) == 2
        # Most recent first
        assert history[0].status == JobStatus.RUNNING

    async def test_get_history_limit(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution]
    ):
        history = await job_repo.get_history("fetch_draws", limit=1)
        assert len(history) == 1

    async def test_cleanup_old(
        self, job_repo: JobRepository, sample_jobs: list[JobExecution], db_session
    ):
        cutoff = datetime.utcnow() - timedelta(days=90)
        deleted = await job_repo.cleanup_old(cutoff)
        assert deleted == 1  # Only the 100-day old job

        # Verify it's actually gone
        remaining = await job_repo.get_all()
        assert len(remaining) == 3
