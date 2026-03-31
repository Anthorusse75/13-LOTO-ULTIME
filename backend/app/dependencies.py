from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any

from fastapi import Depends, HTTPException, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.game_definitions import GameConfig, load_all_game_configs
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
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


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


# ── Game config resolution ──

_game_configs_by_slug = load_all_game_configs()


async def get_game_config(
    game_id: int = Path(..., gt=0),
    game_repo: GameRepository = Depends(get_game_repository),
) -> GameConfig:
    """Resolve game_id → GameConfig via DB lookup + YAML configs."""
    game = await game_repo.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    cfg = _game_configs_by_slug.get(game.slug)
    if cfg is not None:
        return cfg
    # Fallback: build GameConfig from DB record (e.g. for test games)
    return GameConfig(
        name=game.name,
        slug=game.slug,
        numbers_pool=game.numbers_pool,
        numbers_drawn=game.numbers_drawn,
        min_number=game.min_number,
        max_number=game.max_number,
        stars_pool=game.stars_pool,
        stars_drawn=game.stars_drawn,
        star_name=game.star_name,
        draw_frequency=game.draw_frequency,
    )


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
            credentials.credentials,
            settings.get_jwt_verify_key(),
            settings.JWT_ALGORITHM,
            previous_secret_key=(
                settings.PREVIOUS_SECRET_KEY if settings.JWT_ALGORITHM == "HS256" else None
            ),
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


def require_role(minimum_role: UserRole) -> Callable[..., Coroutine[Any, Any, User]]:
    """FastAPI dependency that checks the user has the minimum required role."""
    role_hierarchy = {
        UserRole.CONSULTATION: 1,
        UserRole.UTILISATEUR: 2,
        UserRole.ADMIN: 3,
    }

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if role_hierarchy.get(current_user.role, 0) < role_hierarchy[minimum_role]:
            raise AuthorizationError(f"Accès réservé au rôle {minimum_role.value} minimum")
        return current_user

    return role_checker
