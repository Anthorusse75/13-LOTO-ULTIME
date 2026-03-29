"""Tests for scheduler jobs — covers job wrappers and core logic."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — mock get_session as async generator
# ---------------------------------------------------------------------------

def _make_session_ctx(mock_session):
    """Create an async-generator that yields mock_session once then breaks."""

    async def _gen():
        yield mock_session

    return _gen


# ===========================================================================
# compute_scoring
# ===========================================================================


class TestComputeScoringJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.compute_scoring.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.compute_scoring import compute_scoring_job

            await compute_scoring_job(triggered_by="test")
            mock_track.assert_awaited_once()
            assert mock_track.call_args.kwargs["job_name"] == "compute_scoring"

    @pytest.mark.asyncio
    async def test_do_compute_scoring_no_games(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = []

        with (
            patch(
                "app.scheduler.jobs.compute_scoring.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GridRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.load_all_game_configs",
                return_value={},
            ),
        ):
            from app.scheduler.jobs.compute_scoring import _do_compute_scoring

            result = await _do_compute_scoring()
            assert result["games_processed"] == 0

    @pytest.mark.asyncio
    async def test_do_compute_scoring_skips_no_stats(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        mock_stats_repo = AsyncMock()
        mock_stats_repo.get_latest.return_value = None

        config = MagicMock()

        with (
            patch(
                "app.scheduler.jobs.compute_scoring.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GridRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.StatisticsRepository",
                return_value=mock_stats_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.compute_scoring import _do_compute_scoring

            result = await _do_compute_scoring()
            assert result["details"]["loto-fdj"]["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_do_compute_scoring_rescores_grids(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        snapshot = MagicMock(frequencies={}, gaps={}, cooccurrence_matrix={})
        mock_stats_repo = AsyncMock()
        mock_stats_repo.get_latest.return_value = snapshot

        grid = MagicMock(id=10, numbers=[1, 2, 3, 4, 5])
        mock_grid_repo = AsyncMock()
        mock_grid_repo.get_all.return_value = [grid]

        config = MagicMock()
        score_result = MagicMock(total_score=7.5, score_breakdown={"freq": 8.0})

        with (
            patch(
                "app.scheduler.jobs.compute_scoring.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GridRepository",
                return_value=mock_grid_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.StatisticsRepository",
                return_value=mock_stats_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
            patch(
                "app.scheduler.jobs.compute_scoring.GridScorer"
            ) as MockScorer,
        ):
            MockScorer.from_profile.return_value.score.return_value = score_result

            from app.scheduler.jobs.compute_scoring import _do_compute_scoring

            result = await _do_compute_scoring()
            assert result["details"]["loto-fdj"]["status"] == "success"
            assert result["details"]["loto-fdj"]["rescored"] == 1


# ===========================================================================
# compute_statistics
# ===========================================================================


class TestComputeStatsJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.compute_statistics.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.compute_statistics import compute_stats_job

            await compute_stats_job(triggered_by="test")
            mock_track.assert_awaited_once()
            assert mock_track.call_args.kwargs["job_name"] == "compute_stats"

    @pytest.mark.asyncio
    async def test_do_compute_stats_no_games(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = []

        with (
            patch(
                "app.scheduler.jobs.compute_statistics.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.DrawRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.load_all_game_configs",
                return_value={},
            ),
        ):
            from app.scheduler.jobs.compute_statistics import _do_compute_stats

            result = await _do_compute_stats()
            assert result["games_processed"] == 0

    @pytest.mark.asyncio
    async def test_do_compute_stats_success(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        snapshot = MagicMock(id="snap-1", draw_count=100)
        mock_stats_service = AsyncMock()
        mock_stats_service.compute_all.return_value = snapshot
        config = MagicMock()

        with (
            patch(
                "app.scheduler.jobs.compute_statistics.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.DrawRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.StatisticsService",
                return_value=mock_stats_service,
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.compute_statistics import _do_compute_stats

            result = await _do_compute_stats()
            assert result["details"]["loto-fdj"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_do_compute_stats_error(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        mock_stats_service = AsyncMock()
        mock_stats_service.compute_all.side_effect = RuntimeError("boom")
        config = MagicMock()

        with (
            patch(
                "app.scheduler.jobs.compute_statistics.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.DrawRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.StatisticsService",
                return_value=mock_stats_service,
            ),
            patch(
                "app.scheduler.jobs.compute_statistics.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.compute_statistics import _do_compute_stats

            result = await _do_compute_stats()
            assert result["details"]["loto-fdj"]["status"] == "error"


# ===========================================================================
# compute_top_grids
# ===========================================================================


class TestComputeTopGridsJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.compute_top_grids.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.compute_top_grids import compute_top_grids_job

            await compute_top_grids_job(triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_do_compute_top_grids_no_games(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = []

        with (
            patch(
                "app.scheduler.jobs.compute_top_grids.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GridRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.load_all_game_configs",
                return_value={},
            ),
        ):
            from app.scheduler.jobs.compute_top_grids import _do_compute_top_grids

            result = await _do_compute_top_grids()
            assert result["games_processed"] == 0

    @pytest.mark.asyncio
    async def test_do_compute_top_grids_success(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        mock_grid_repo = AsyncMock()
        mock_grid_repo.get_top_grids.return_value = []

        scored_grid = MagicMock(
            numbers=[1, 2, 3, 4, 5],
            total_score=7.0,
            score_breakdown={"freq": 7},
        )
        mock_grid_service = AsyncMock()
        mock_grid_service.generate_grids.return_value = ([scored_grid], "auto", 123.4)

        config = MagicMock()

        with (
            patch(
                "app.scheduler.jobs.compute_top_grids.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GridRepository",
                return_value=mock_grid_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GridService",
                return_value=mock_grid_service,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.compute_top_grids import _do_compute_top_grids

            result = await _do_compute_top_grids()
            assert result["details"]["loto-fdj"]["status"] == "success"
            assert result["details"]["loto-fdj"]["generated"] == 1

    @pytest.mark.asyncio
    async def test_do_compute_top_grids_error(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        mock_grid_repo = AsyncMock()
        mock_grid_repo.get_top_grids.return_value = []

        mock_grid_service = AsyncMock()
        mock_grid_service.generate_grids.side_effect = RuntimeError("fail")

        config = MagicMock()

        with (
            patch(
                "app.scheduler.jobs.compute_top_grids.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.StatisticsRepository",
                return_value=AsyncMock(),
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GridRepository",
                return_value=mock_grid_repo,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.GridService",
                return_value=mock_grid_service,
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.compute_top_grids import _do_compute_top_grids

            result = await _do_compute_top_grids()
            assert result["details"]["loto-fdj"]["status"] == "error"


# ===========================================================================
# fetch_draws
# ===========================================================================


class TestFetchDrawsJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo.get_by_slug.return_value = mock_game

        with (
            patch(
                "app.scheduler.jobs.fetch_draws.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.fetch_draws.GameRepository",
                return_value=mock_game_repo,
            ),
            patch(
                "app.scheduler.jobs.fetch_draws.execute_with_tracking",
                new_callable=AsyncMock,
            ) as mock_track,
        ):
            from app.scheduler.jobs.fetch_draws import fetch_draws_job

            await fetch_draws_job("loto-fdj", triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_job_game_not_found(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game_repo.get_by_slug.return_value = None

        with (
            patch(
                "app.scheduler.jobs.fetch_draws.get_session",
                _make_session_ctx(mock_session),
            ),
            patch(
                "app.scheduler.jobs.fetch_draws.GameRepository",
                return_value=mock_game_repo,
            ),
        ):
            from app.scheduler.jobs.fetch_draws import fetch_draws_job

            # Should return early without tracking
            await fetch_draws_job("unknown-game", triggered_by="test")

    @pytest.mark.asyncio
    async def test_do_fetch_circuit_open(self):
        mock_cb = MagicMock()
        mock_cb.allow_request.return_value = False

        with patch(
            "app.scheduler.jobs.fetch_draws.get_circuit_breaker",
            return_value=mock_cb,
        ):
            from app.scheduler.jobs.fetch_draws import _do_fetch

            result = await _do_fetch("loto-fdj")
            assert result["skipped"] is True
            assert result["reason"] == "circuit_breaker_open"

    @pytest.mark.asyncio
    async def test_do_fetch_success(self):
        mock_session = AsyncMock()
        mock_cb = MagicMock()
        mock_cb.allow_request.return_value = True

        mock_game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_by_slug.return_value = mock_game

        mock_draw_repo = AsyncMock()
        mock_draw_repo.get_latest.return_value = []
        mock_draw_repo.exists.return_value = False

        raw_draw = MagicMock(draw_date="2024-01-01", draw_number=1, numbers=[1, 2, 3, 4, 5], stars=[1])
        mock_scraper = AsyncMock()
        mock_scraper.fetch_latest_draws.return_value = [raw_draw]

        validated = MagicMock(draw_date="2024-01-01", draw_number=1, numbers=[1, 2, 3, 4, 5], stars=[1])
        mock_validator = MagicMock()
        mock_validator.validate.return_value = validated

        config = MagicMock(
            min_number=1, max_number=49, numbers_drawn=5,
            stars_pool=10, stars_drawn=1,
        )

        with (
            patch("app.scheduler.jobs.fetch_draws.get_circuit_breaker", return_value=mock_cb),
            patch("app.scheduler.jobs.fetch_draws.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.fetch_draws.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.fetch_draws.DrawRepository", return_value=mock_draw_repo),
            patch("app.scheduler.jobs.fetch_draws.get_scraper", return_value=mock_scraper),
            patch("app.scheduler.jobs.fetch_draws.DrawValidator", return_value=mock_validator),
            patch(
                "app.scheduler.jobs.fetch_draws.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.fetch_draws import _do_fetch

            result = await _do_fetch("loto-fdj")
            assert result["fetched"] == 1
            assert result["saved"] == 1
            assert result["duplicates"] == 0

    @pytest.mark.asyncio
    async def test_do_fetch_duplicate(self):
        mock_session = AsyncMock()
        mock_cb = MagicMock()
        mock_cb.allow_request.return_value = True

        mock_game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_by_slug.return_value = mock_game

        mock_draw_repo = AsyncMock()
        mock_draw_repo.get_latest.return_value = []
        mock_draw_repo.exists.return_value = True  # already exists

        raw_draw = MagicMock()
        mock_scraper = AsyncMock()
        mock_scraper.fetch_latest_draws.return_value = [raw_draw]

        validated = MagicMock(draw_date="2024-01-01")
        mock_validator = MagicMock()
        mock_validator.validate.return_value = validated

        config = MagicMock(
            min_number=1, max_number=49, numbers_drawn=5,
            stars_pool=10, stars_drawn=1,
        )

        with (
            patch("app.scheduler.jobs.fetch_draws.get_circuit_breaker", return_value=mock_cb),
            patch("app.scheduler.jobs.fetch_draws.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.fetch_draws.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.fetch_draws.DrawRepository", return_value=mock_draw_repo),
            patch("app.scheduler.jobs.fetch_draws.get_scraper", return_value=mock_scraper),
            patch("app.scheduler.jobs.fetch_draws.DrawValidator", return_value=mock_validator),
            patch(
                "app.scheduler.jobs.fetch_draws.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.fetch_draws import _do_fetch

            result = await _do_fetch("loto-fdj")
            assert result["duplicates"] == 1
            assert result["saved"] == 0

    @pytest.mark.asyncio
    async def test_do_fetch_validation_error(self):
        mock_session = AsyncMock()
        mock_cb = MagicMock()
        mock_cb.allow_request.return_value = True

        mock_game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_by_slug.return_value = mock_game

        mock_draw_repo = AsyncMock()
        mock_draw_repo.get_latest.return_value = []

        raw_draw = MagicMock()
        mock_scraper = AsyncMock()
        mock_scraper.fetch_latest_draws.return_value = [raw_draw]

        mock_validator = MagicMock()
        mock_validator.validate.side_effect = ValueError("bad data")

        config = MagicMock(
            min_number=1, max_number=49, numbers_drawn=5,
            stars_pool=10, stars_drawn=1,
        )

        with (
            patch("app.scheduler.jobs.fetch_draws.get_circuit_breaker", return_value=mock_cb),
            patch("app.scheduler.jobs.fetch_draws.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.fetch_draws.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.fetch_draws.DrawRepository", return_value=mock_draw_repo),
            patch("app.scheduler.jobs.fetch_draws.get_scraper", return_value=mock_scraper),
            patch("app.scheduler.jobs.fetch_draws.DrawValidator", return_value=mock_validator),
            patch(
                "app.scheduler.jobs.fetch_draws.load_all_game_configs",
                return_value={"loto-fdj": config},
            ),
        ):
            from app.scheduler.jobs.fetch_draws import _do_fetch

            result = await _do_fetch("loto-fdj")
            assert result["validation_errors"] == 1


# ===========================================================================
# optimize_portfolio
# ===========================================================================


class TestOptimizePortfolioJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.optimize_portfolio.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.optimize_portfolio import optimize_portfolio_job

            await optimize_portfolio_job(triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_do_optimize_portfolio_no_games(self):
        mock_session = AsyncMock()
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = []

        with (
            patch("app.scheduler.jobs.optimize_portfolio.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.optimize_portfolio.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.optimize_portfolio.StatisticsRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.GridRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.PortfolioRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.load_all_game_configs", return_value={}),
        ):
            from app.scheduler.jobs.optimize_portfolio import _do_optimize_portfolio

            result = await _do_optimize_portfolio()
            assert result["games_processed"] == 0

    @pytest.mark.asyncio
    async def test_do_optimize_portfolio_success(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        scored_grid = MagicMock(numbers=[1, 2, 3, 4, 5], total_score=7.0)
        portfolio_result = MagicMock(
            grids=[scored_grid],
            diversity_score=0.85,
            coverage_score=0.9,
        )
        mock_grid_service = AsyncMock()
        mock_grid_service.generate_portfolio.return_value = (portfolio_result, "balanced", 50.0)

        config = MagicMock()

        with (
            patch("app.scheduler.jobs.optimize_portfolio.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.optimize_portfolio.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.optimize_portfolio.StatisticsRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.GridRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.PortfolioRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.optimize_portfolio.GridService", return_value=mock_grid_service),
            patch("app.scheduler.jobs.optimize_portfolio.load_all_game_configs", return_value={"loto-fdj": config}),
        ):
            from app.scheduler.jobs.optimize_portfolio import _do_optimize_portfolio

            result = await _do_optimize_portfolio()
            assert "loto-fdj" in result["details"]
            # Should have results for 4 strategies
            assert len(result["details"]["loto-fdj"]) == 4


# ===========================================================================
# cleanup
# ===========================================================================


class TestCleanupJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.cleanup.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.cleanup import cleanup_job

            await cleanup_job(triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_do_cleanup(self):
        mock_result = MagicMock(rowcount=5)
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "app.scheduler.jobs.cleanup.get_session",
            _make_session_ctx(mock_session),
        ):
            from app.scheduler.jobs.cleanup import _do_cleanup

            result = await _do_cleanup()
            assert result["jobs_deleted"] == 5
            assert result["snapshots_deleted"] == 5
            assert result["grids_deleted"] == 5
            assert result["portfolios_deleted"] == 5
            assert mock_session.execute.call_count == 4


# ===========================================================================
# health_check
# ===========================================================================


class TestHealthCheckJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.health_check.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.health_check import health_check_job

            await health_check_job(triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_do_health_check_healthy(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        # Recent draw — not stale
        draw = MagicMock(draw_date=datetime.now(UTC).date())
        mock_draw_repo = AsyncMock()
        mock_draw_repo.get_latest.return_value = [draw]

        mock_job_repo = AsyncMock()
        mock_job_repo.get_running_jobs.return_value = []

        with (
            patch("app.scheduler.jobs.health_check.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.health_check.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.health_check.DrawRepository", return_value=mock_draw_repo),
            patch("app.scheduler.jobs.health_check.JobRepository", return_value=mock_job_repo),
        ):
            from app.scheduler.jobs.health_check import _do_health_check

            result = await _do_health_check()
            assert result["status"] == "healthy"
            assert result["checks"]["active_games"] == 1
            assert result["checks"]["stale_games"] == []

    @pytest.mark.asyncio
    async def test_do_health_check_stale_game(self):
        mock_session = AsyncMock()

        game = MagicMock(id=1, slug="loto-fdj")
        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = [game]

        # Old draw — stale
        old_date = (datetime.now(UTC) - timedelta(days=30)).date()
        draw = MagicMock(draw_date=old_date)
        mock_draw_repo = AsyncMock()
        mock_draw_repo.get_latest.return_value = [draw]

        mock_job_repo = AsyncMock()
        mock_job_repo.get_running_jobs.return_value = []

        with (
            patch("app.scheduler.jobs.health_check.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.health_check.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.health_check.DrawRepository", return_value=mock_draw_repo),
            patch("app.scheduler.jobs.health_check.JobRepository", return_value=mock_job_repo),
        ):
            from app.scheduler.jobs.health_check import _do_health_check

            result = await _do_health_check()
            assert result["status"] == "warning"
            assert "loto-fdj" in result["checks"]["stale_games"]

    @pytest.mark.asyncio
    async def test_do_health_check_stuck_job(self):
        mock_session = AsyncMock()

        mock_game_repo = AsyncMock()
        mock_game_repo.get_active_games.return_value = []

        stuck_job = MagicMock(
            job_name="fetch_draws",
            started_at=datetime.now(UTC) - timedelta(hours=3),
        )
        mock_job_repo = AsyncMock()
        mock_job_repo.get_running_jobs.return_value = [stuck_job]

        with (
            patch("app.scheduler.jobs.health_check.get_session", _make_session_ctx(mock_session)),
            patch("app.scheduler.jobs.health_check.GameRepository", return_value=mock_game_repo),
            patch("app.scheduler.jobs.health_check.DrawRepository", return_value=AsyncMock()),
            patch("app.scheduler.jobs.health_check.JobRepository", return_value=mock_job_repo),
        ):
            from app.scheduler.jobs.health_check import _do_health_check

            result = await _do_health_check()
            assert result["status"] == "warning"
            assert "fetch_draws" in result["checks"]["stuck_jobs"]


# ===========================================================================
# nightly_pipeline
# ===========================================================================


class TestNightlyPipelineJob:
    @pytest.mark.asyncio
    async def test_job_delegates_to_tracker(self):
        with patch(
            "app.scheduler.jobs.nightly_pipeline.execute_with_tracking",
            new_callable=AsyncMock,
        ) as mock_track:
            from app.scheduler.jobs.nightly_pipeline import nightly_pipeline_job

            await nightly_pipeline_job(triggered_by="test")
            mock_track.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_do_nightly_pipeline_all_success(self):
        with (
            patch(
                "app.scheduler.jobs.nightly_pipeline._do_nightly_pipeline.__module__",
                create=True,
            ) if False else patch(
                "app.scheduler.jobs.fetch_draws._do_fetch",
                new_callable=AsyncMock,
                return_value={"fetched": 5},
            ),
            patch(
                "app.scheduler.jobs.compute_statistics._do_compute_stats",
                new_callable=AsyncMock,
                return_value={"games_processed": 1},
            ),
            patch(
                "app.scheduler.jobs.compute_scoring._do_compute_scoring",
                new_callable=AsyncMock,
                return_value={"games_processed": 1},
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids._do_compute_top_grids",
                new_callable=AsyncMock,
                return_value={"games_processed": 1},
            ),
            patch(
                "app.scheduler.jobs.optimize_portfolio._do_optimize_portfolio",
                new_callable=AsyncMock,
                return_value={"games_processed": 1},
            ),
        ):
            from app.scheduler.jobs.nightly_pipeline import _do_nightly_pipeline

            result = await _do_nightly_pipeline()
            assert result["steps"] == 7
            for step in result["details"].values():
                assert step["status"] == "success"

    @pytest.mark.asyncio
    async def test_do_nightly_pipeline_step_failure(self):
        with (
            patch(
                "app.scheduler.jobs.fetch_draws._do_fetch",
                new_callable=AsyncMock,
                side_effect=RuntimeError("scraper down"),
            ),
            patch(
                "app.scheduler.jobs.compute_statistics._do_compute_stats",
                new_callable=AsyncMock,
                return_value={},
            ),
            patch(
                "app.scheduler.jobs.compute_scoring._do_compute_scoring",
                new_callable=AsyncMock,
                return_value={},
            ),
            patch(
                "app.scheduler.jobs.compute_top_grids._do_compute_top_grids",
                new_callable=AsyncMock,
                return_value={},
            ),
            patch(
                "app.scheduler.jobs.optimize_portfolio._do_optimize_portfolio",
                new_callable=AsyncMock,
                return_value={},
            ),
        ):
            from app.scheduler.jobs.nightly_pipeline import _do_nightly_pipeline

            result = await _do_nightly_pipeline()
            # fetch_loto should fail, others succeed
            assert result["details"]["fetch_loto"]["status"] == "error"
            assert result["details"]["compute_stats"]["status"] == "success"
