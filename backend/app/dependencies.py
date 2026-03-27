from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_session
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.repositories.grid_repository import GridRepository
from app.repositories.job_repository import JobRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.user_repository import UserRepository
from app.services.statistics import StatisticsService

# ── Database session ──


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


# ── Repositories ──


def get_game_repository(session: AsyncSession = Depends(get_db)) -> GameRepository:
    return GameRepository(session)


def get_draw_repository(session: AsyncSession = Depends(get_db)) -> DrawRepository:
    return DrawRepository(session)


def get_statistics_repository(
    session: AsyncSession = Depends(get_db),
) -> StatisticsRepository:
    return StatisticsRepository(session)


def get_grid_repository(session: AsyncSession = Depends(get_db)) -> GridRepository:
    return GridRepository(session)


def get_portfolio_repository(
    session: AsyncSession = Depends(get_db),
) -> PortfolioRepository:
    return PortfolioRepository(session)


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_job_repository(session: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(session)


# ── Services ──


def get_statistics_service(
    draw_repo: DrawRepository = Depends(get_draw_repository),
    stats_repo: StatisticsRepository = Depends(get_statistics_repository),
) -> StatisticsService:
    return StatisticsService(draw_repo, stats_repo)
