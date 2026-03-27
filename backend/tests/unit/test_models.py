"""Tests for SQLAlchemy models."""

from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.models.game import GameDefinition
from app.models.grid import ScoredGrid
from app.models.job import JobExecution, JobStatus
from app.models.portfolio import Portfolio
from app.models.statistics import StatisticsSnapshot
from app.models.user import User, UserRole


class TestGameDefinitionModel:
    async def test_create_game(self, db_session: AsyncSession):
        game = GameDefinition(
            name="Test Loto",
            slug="test-loto",
            numbers_pool=49,
            numbers_drawn=5,
            min_number=1,
            max_number=49,
            stars_pool=10,
            stars_drawn=1,
            draw_frequency="lun/mer/sam",
            historical_source="test",
        )
        db_session.add(game)
        await db_session.flush()
        assert game.id is not None
        assert game.is_active is True

    async def test_game_repr(self, sample_game: GameDefinition):
        assert "loto-fdj" in repr(sample_game)


class TestDrawModel:
    async def test_create_draw(self, db_session: AsyncSession, sample_game: GameDefinition):
        draw = Draw(
            game_id=sample_game.id,
            draw_date=date(2026, 3, 1),
            draw_number=100,
            numbers=[1, 7, 23, 34, 45],
            stars=[3],
        )
        db_session.add(draw)
        await db_session.flush()
        assert draw.id is not None
        assert draw.numbers == [1, 7, 23, 34, 45]

    async def test_draw_repr(self, db_session: AsyncSession, sample_game: GameDefinition):
        draw = Draw(
            game_id=sample_game.id,
            draw_date=date(2026, 3, 2),
            numbers=[5, 10, 15, 20, 25],
        )
        db_session.add(draw)
        await db_session.flush()
        assert "numbers=" in repr(draw)


class TestUserModel:
    async def test_create_user(self, db_session: AsyncSession):
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpwd",
            role=UserRole.UTILISATEUR,
        )
        db_session.add(user)
        await db_session.flush()
        assert user.id is not None
        assert user.role == UserRole.UTILISATEUR
        assert user.is_active is True

    def test_user_roles(self):
        assert UserRole.ADMIN == "ADMIN"
        assert UserRole.UTILISATEUR == "UTILISATEUR"
        assert UserRole.CONSULTATION == "CONSULTATION"


class TestJobExecutionModel:
    async def test_create_job(self, db_session: AsyncSession):
        job = JobExecution(
            job_name="fetch_draws",
            status=JobStatus.RUNNING,
            started_at=datetime(2026, 3, 1, 12, 0),
            triggered_by="scheduler",
        )
        db_session.add(job)
        await db_session.flush()
        assert job.id is not None
        assert job.status == JobStatus.RUNNING

    def test_job_statuses(self):
        assert JobStatus.PENDING == "PENDING"
        assert JobStatus.SUCCESS == "SUCCESS"
        assert JobStatus.FAILED == "FAILED"


class TestStatisticsSnapshotModel:
    async def test_create_snapshot(self, db_session: AsyncSession, sample_game: GameDefinition):
        snapshot = StatisticsSnapshot(
            game_id=sample_game.id,
            computed_at=datetime(2026, 3, 1, 12, 0),
            draw_count=100,
            frequencies={"1": {"count": 20}},
            gaps={"1": {"current_gap": 3}},
            cooccurrence_matrix={"1-2": 5},
            temporal_trends={"hot": [1, 2, 3]},
            bayesian_priors={"1": {"alpha": 20}},
            graph_metrics={"centrality": {}},
            distribution_stats={"entropy": 5.6},
        )
        db_session.add(snapshot)
        await db_session.flush()
        assert snapshot.id is not None


class TestScoredGridModel:
    async def test_create_grid(self, db_session: AsyncSession, sample_game: GameDefinition):
        grid = ScoredGrid(
            game_id=sample_game.id,
            numbers=[3, 12, 25, 37, 44],
            stars=[7],
            total_score=8.5,
            score_breakdown={"frequency": 0.8, "gap": 0.7},
            method="genetic_algorithm",
            computed_at=datetime(2026, 3, 1),
        )
        db_session.add(grid)
        await db_session.flush()
        assert grid.id is not None
        assert grid.is_top is False


class TestPortfolioModel:
    async def test_create_portfolio(self, db_session: AsyncSession, sample_game: GameDefinition):
        portfolio = Portfolio(
            game_id=sample_game.id,
            name="Test Portfolio",
            strategy="balanced",
            grid_count=5,
            grids=[{"numbers": [1, 2, 3, 4, 5], "score": 7.5}],
            diversity_score=0.85,
            coverage_score=0.72,
            avg_grid_score=7.5,
            computed_at=datetime(2026, 3, 1),
        )
        db_session.add(portfolio)
        await db_session.flush()
        assert portfolio.id is not None
