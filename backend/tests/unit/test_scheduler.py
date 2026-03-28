"""Unit tests for the scheduler configuration."""


class TestSchedulerCreation:
    """Tests for scheduler setup and job registration."""

    def test_create_scheduler_registers_jobs(self):
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SECRET_KEY="test-secret-key-for-testing-min-32-chars!!",
            SCHEDULER_ENABLED=True,
        )

        from app.scheduler.scheduler import create_scheduler

        scheduler = create_scheduler(settings)
        jobs = scheduler.get_jobs()

        # Should have 4 jobs registered (nightly_pipeline, cleanup, health_check, backup_db)
        assert len(jobs) == 4

        job_ids = {j.id for j in jobs}
        assert "nightly_pipeline" in job_ids
        assert "cleanup" in job_ids
        assert "health_check" in job_ids
        assert "backup_db" in job_ids

    def test_scheduler_job_defaults(self):
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SECRET_KEY="test-secret-key-for-testing-min-32-chars!!",
        )

        from app.scheduler.scheduler import create_scheduler

        scheduler = create_scheduler(settings)

        # Verify job_defaults are set on the scheduler
        assert scheduler._job_defaults["max_instances"] == 1
        assert scheduler._job_defaults["misfire_grace_time"] == 3600
        assert scheduler._job_defaults["coalesce"] is True

    def test_scheduler_not_started_on_creation(self):
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SECRET_KEY="test-secret-key-for-testing-min-32-chars!!",
        )

        from app.scheduler.scheduler import create_scheduler

        scheduler = create_scheduler(settings)
        assert not scheduler.running

    def test_nightly_pipeline_cron_schedule(self):
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SECRET_KEY="test-secret-key-for-testing-min-32-chars!!",
        )

        from app.scheduler.scheduler import create_scheduler

        scheduler = create_scheduler(settings)
        pipeline = scheduler.get_job("nightly_pipeline")

        assert pipeline is not None
        trigger = pipeline.trigger
        # Verify it's a cron trigger
        assert trigger.__class__.__name__ == "CronTrigger"

    def test_health_check_interval_schedule(self):
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SECRET_KEY="test-secret-key-for-testing-min-32-chars!!",
        )

        from app.scheduler.scheduler import create_scheduler

        scheduler = create_scheduler(settings)
        health_check = scheduler.get_job("health_check")

        assert health_check is not None
        trigger = health_check.trigger
        assert trigger.__class__.__name__ == "IntervalTrigger"
