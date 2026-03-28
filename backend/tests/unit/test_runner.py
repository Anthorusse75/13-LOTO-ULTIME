"""Unit tests for the job execution runner."""

from unittest.mock import AsyncMock, patch

import pytest

from app.models.job import JobStatus


class TestExecuteWithTracking:
    """Tests for the execute_with_tracking function."""

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        # merge should return the object passed to it
        session.merge = AsyncMock(side_effect=lambda obj: obj)
        return session

    @pytest.fixture
    def mock_get_session(self, mock_session):
        async def _gen():
            yield mock_session

        return _gen

    @pytest.mark.asyncio
    async def test_successful_execution(self, mock_get_session, mock_session):
        from app.scheduler.runner import execute_with_tracking

        mock_session.add = lambda obj: None

        async def dummy_func():
            return {"result": "ok"}

        with patch("app.scheduler.runner.get_session", mock_get_session):
            result = await execute_with_tracking(
                job_name="test_job",
                func=dummy_func,
                triggered_by="test",
            )

        assert result.status == JobStatus.SUCCESS
        assert result.result_summary == {"result": "ok"}
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_retries_on_failure(self, mock_get_session, mock_session):
        from app.scheduler.runner import execute_with_tracking

        mock_session.add = lambda obj: None

        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("Temporary failure")
            return {"attempt": call_count}

        with (
            patch("app.scheduler.runner.get_session", mock_get_session),
            patch("app.scheduler.runner.RETRY_DELAYS", [0, 0, 0]),
        ):
            result = await execute_with_tracking(
                job_name="flaky_job",
                func=flaky_func,
                triggered_by="test",
            )

        assert result.status == JobStatus.SUCCESS
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_get_session, mock_session):
        from app.scheduler.runner import execute_with_tracking

        mock_session.add = lambda obj: None

        async def always_fails():
            raise RuntimeError("Permanent failure")

        with (
            patch("app.scheduler.runner.get_session", mock_get_session),
            patch("app.scheduler.runner.RETRY_DELAYS", [0, 0, 0]),
        ):
            result = await execute_with_tracking(
                job_name="failing_job",
                func=always_fails,
                triggered_by="test",
            )

        assert result.status == JobStatus.FAILED
        assert "Permanent failure" in result.error_message

    @pytest.mark.asyncio
    async def test_tracks_duration(self, mock_get_session, mock_session):
        import asyncio

        from app.scheduler.runner import execute_with_tracking

        mock_session.add = lambda obj: None

        async def slow_func():
            await asyncio.sleep(0.05)
            return {}

        with patch("app.scheduler.runner.get_session", mock_get_session):
            result = await execute_with_tracking(
                job_name="slow_job",
                func=slow_func,
                triggered_by="test",
            )

        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0.04

    @pytest.mark.asyncio
    async def test_game_id_passed(self, mock_get_session, mock_session):
        from app.scheduler.runner import execute_with_tracking

        mock_session.add = lambda obj: None

        async def dummy():
            return {}

        with patch("app.scheduler.runner.get_session", mock_get_session):
            result = await execute_with_tracking(
                job_name="test_with_game",
                func=dummy,
                game_id=42,
                triggered_by="manual",
            )

        assert result.game_id == 42
        assert result.triggered_by == "manual"
