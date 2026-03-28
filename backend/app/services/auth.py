"""Authentication service — login, register, token management."""

from datetime import UTC, datetime

import structlog

from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger("auth")


class AuthService:
    def __init__(self, user_repo: UserRepository, settings: Settings):
        self._user_repo = user_repo
        self._settings = settings

    async def login(self, username: str, password: str) -> tuple[str, str, User]:
        """Authenticate user and return (access_token, refresh_token, user)."""
        user = await self._user_repo.get_by_email(username)
        if user is None:
            user = await self._user_repo.get_by_username(username)

        if user is None or not verify_password(password, user.hashed_password):
            logger.warning("login.failed", username=username)
            raise AuthenticationError("Identifiants incorrects")

        if not user.is_active:
            logger.warning("login.inactive_user", username=username)
            raise AuthenticationError("Compte désactivé")

        # Update last_login
        user.last_login = datetime.now(UTC)
        await self._user_repo.update(user)

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        logger.info("login.success", user_id=user.id, username=user.username)
        return access_token, refresh_token, user

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.CONSULTATION,
    ) -> User:
        """Register a new user."""
        # Check uniqueness
        if await self._user_repo.get_by_username(username):
            raise AuthenticationError(f"Le nom d'utilisateur '{username}' est déjà pris")
        if await self._user_repo.get_by_email(email):
            raise AuthenticationError(f"L'email '{email}' est déjà utilisé")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            is_active=True,
        )
        user = await self._user_repo.create(user)

        logger.info("register.success", user_id=user.id, username=username, role=role.value)
        return user

    async def refresh(self, user_id: int) -> tuple[str, str]:
        """Issue new tokens for a valid refresh token's user."""
        user = await self._user_repo.get(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Utilisateur invalide ou désactivé")

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        return access_token, refresh_token

    def _create_access_token(self, user: User) -> str:
        return create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            secret_key=self._settings.SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_EXPIRATION_MINUTES,
        )

    def _create_refresh_token(self, user: User) -> str:
        return create_refresh_token(
            data={"sub": str(user.id)},
            secret_key=self._settings.SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )


async def create_initial_admin(user_repo: UserRepository, settings: Settings) -> None:
    """Create or update the initial admin user at startup."""
    count = await user_repo.count()
    if count > 0:
        # Ensure the admin matches current env settings
        admin = await user_repo.get_by_username("admin")
        if admin and admin.email != settings.ADMIN_EMAIL:
            admin.email = settings.ADMIN_EMAIL
            admin.hashed_password = hash_password(settings.ADMIN_INITIAL_PASSWORD)
            await user_repo.update(admin)
            logger.info("initial_admin.updated", email=settings.ADMIN_EMAIL)
        return

    admin = User(
        username="admin",
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_INITIAL_PASSWORD),
        role=UserRole.ADMIN,
        is_active=True,
    )
    await user_repo.create(admin)
    logger.info(
        "initial_admin.created",
        username="admin",
        email=settings.ADMIN_EMAIL,
    )
