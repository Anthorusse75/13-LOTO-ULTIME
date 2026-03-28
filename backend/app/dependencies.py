from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.models.base import get_session
from app.models.user import User, UserRole
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.repositories.grid_repository import GridRepository
from app.repositories.job_repository import JobRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService
from app.services.grid import GridService
from app.services.simulation import SimulationService
from app.services.statistics import StatisticsService

# ── Database session ──

_bearer = HTTPBearer(auto_error=False)


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


def get_grid_service(
    stats_repo: StatisticsRepository = Depends(get_statistics_repository),
    grid_repo: GridRepository = Depends(get_grid_repository),
    portfolio_repo: PortfolioRepository = Depends(get_portfolio_repository),
) -> GridService:
    return GridService(stats_repo, grid_repo, portfolio_repo)


def get_simulation_service(
    draw_repo: DrawRepository = Depends(get_draw_repository),
    stats_repo: StatisticsRepository = Depends(get_statistics_repository),
) -> SimulationService:
    return SimulationService(draw_repo, stats_repo)


# ── Auth ──


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repo, settings)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    user_repo: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> User:
    """Decode JWT and return the authenticated user."""
    if credentials is None:
        raise AuthenticationError("Token manquant")

    try:
        payload = decode_access_token(
            credentials.credentials, settings.SECRET_KEY, settings.JWT_ALGORITHM
        )
        if payload.get("type") != "access":
            raise AuthenticationError("Type de token invalide")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Token invalide ou expiré") from exc

    user = await user_repo.get(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Utilisateur inactif ou inexistant")

    return user


def require_role(minimum_role: UserRole):
    """FastAPI dependency that checks the user has the minimum required role."""
    ROLE_HIERARCHY = {
        UserRole.CONSULTATION: 1,
        UserRole.UTILISATEUR: 2,
        UserRole.ADMIN: 3,
    }

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if ROLE_HIERARCHY.get(current_user.role, 0) < ROLE_HIERARCHY[minimum_role]:
            raise AuthorizationError(f"Accès réservé au rôle {minimum_role.value} minimum")
        return current_user

    return role_checker
