"""Tests for authentication: login, register, JWT, RBAC, refresh."""

import pytest

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User, UserRole

# ── Fixtures ──


@pytest.fixture
async def admin_user(db_session) -> User:
    """Create an admin user in the test DB."""
    user = User(
        username="admin",
        email="admin@test.local",
        hashed_password=hash_password("Admin1234!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def regular_user(db_session) -> User:
    """Create a UTILISATEUR user in the test DB."""
    user = User(
        username="user1",
        email="user1@test.local",
        hashed_password=hash_password("User1234!"),
        role=UserRole.UTILISATEUR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def consult_user(db_session) -> User:
    """Create a CONSULTATION user in the test DB."""
    user = User(
        username="viewer",
        email="viewer@test.local",
        hashed_password=hash_password("View1234!"),
        role=UserRole.CONSULTATION,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


SECRET = "test-secret-key-for-testing-min-32-chars!!"


def _make_token(user: User, token_type: str = "access") -> str:
    if token_type == "access":
        return create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            secret_key=SECRET,
        )
    return create_refresh_token(
        data={"sub": str(user.id)},
        secret_key=SECRET,
    )


def _auth_header(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token(user)}"}


# ── Auth Service Tests ──


class TestAuthService:
    @pytest.mark.asyncio
    async def test_login_success(self, db_session, admin_user):
        from app.core.config import Settings
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        access, refresh, user = await service.login("admin", "Admin1234!")
        assert access
        assert refresh
        assert user.username == "admin"

    @pytest.mark.asyncio
    async def test_login_by_email(self, db_session, admin_user):
        from app.core.config import Settings
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        access, refresh, user = await service.login("admin@test.local", "Admin1234!")
        assert user.email == "admin@test.local"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, db_session, admin_user):
        from app.core.config import Settings
        from app.core.exceptions import AuthenticationError
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        with pytest.raises(AuthenticationError):
            await service.login("admin", "WrongPass1!")

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, db_session, admin_user):
        from app.core.config import Settings
        from app.core.exceptions import AuthenticationError
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        with pytest.raises(AuthenticationError):
            await service.login("nobody", "Test1234!")

    @pytest.mark.asyncio
    async def test_register_success(self, db_session, admin_user):
        from app.core.config import Settings
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        user = await service.register(
            "newuser", "new@test.local", "NewPass123!", UserRole.UTILISATEUR
        )
        assert user.username == "newuser"
        assert user.role == UserRole.UTILISATEUR

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, db_session, admin_user):
        from app.core.config import Settings
        from app.core.exceptions import AuthenticationError
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        with pytest.raises(AuthenticationError, match="déjà pris"):
            await service.register("admin", "other@test.local", "NewPass123!")

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, admin_user):
        from app.core.config import Settings
        from app.core.exceptions import AuthenticationError
        from app.repositories.user_repository import UserRepository
        from app.services.auth import AuthService

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        service = AuthService(repo, settings)

        with pytest.raises(AuthenticationError, match="déjà utilisé"):
            await service.register("other", "admin@test.local", "NewPass123!")


# ── Initial Admin Seeding ──


class TestInitialAdmin:
    @pytest.mark.asyncio
    async def test_creates_admin_when_no_users(self, db_session):
        from app.core.config import Settings
        from app.repositories.user_repository import UserRepository
        from app.services.auth import create_initial_admin

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            ADMIN_EMAIL="test@admin.local",
            ADMIN_INITIAL_PASSWORD="TestAdmin1!",
        )

        await create_initial_admin(repo, settings)

        admin = await repo.get_by_username("admin")
        assert admin is not None
        assert admin.role == UserRole.ADMIN
        assert admin.email == "test@admin.local"

    @pytest.mark.asyncio
    async def test_skips_when_users_exist(self, db_session, admin_user):
        from app.core.config import Settings
        from app.repositories.user_repository import UserRepository
        from app.services.auth import create_initial_admin

        repo = UserRepository(db_session)
        settings = Settings(
            SECRET_KEY=SECRET,
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )

        count_before = await repo.count()
        await create_initial_admin(repo, settings)
        count_after = await repo.count()
        assert count_before == count_after


# ── Password Validation ──


class TestPasswordValidation:
    def test_valid_password(self):
        from app.schemas.user import UserCreate

        u = UserCreate(username="abc", email="a@b.c", password="ValidPass1!")
        assert u.password == "ValidPass1!"

    def test_no_uppercase(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValueError, match="majuscule"):
            UserCreate(username="abc", email="a@b.c", password="lowercase1!")

    def test_no_lowercase(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValueError, match="minuscule"):
            UserCreate(username="abc", email="a@b.c", password="UPPERCASE1!")

    def test_no_digit(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValueError, match="chiffre"):
            UserCreate(username="abc", email="a@b.c", password="NoDigitHere!")


# ── RBAC Dependency ──


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_admin_passes_admin_check(self, db_session, admin_user):

        from app.dependencies import require_role

        checker = require_role(UserRole.ADMIN)
        result = await checker(current_user=admin_user)
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_user_fails_admin_check(self, db_session, regular_user):
        from app.core.exceptions import AuthorizationError
        from app.dependencies import require_role

        checker = require_role(UserRole.ADMIN)
        with pytest.raises(AuthorizationError):
            await checker(current_user=regular_user)

    @pytest.mark.asyncio
    async def test_user_passes_user_check(self, db_session, regular_user):
        from app.dependencies import require_role

        checker = require_role(UserRole.UTILISATEUR)
        result = await checker(current_user=regular_user)
        assert result == regular_user

    @pytest.mark.asyncio
    async def test_consult_fails_user_check(self, db_session, consult_user):
        from app.core.exceptions import AuthorizationError
        from app.dependencies import require_role

        checker = require_role(UserRole.UTILISATEUR)
        with pytest.raises(AuthorizationError):
            await checker(current_user=consult_user)

    @pytest.mark.asyncio
    async def test_admin_passes_user_check(self, db_session, admin_user):
        from app.dependencies import require_role

        checker = require_role(UserRole.UTILISATEUR)
        result = await checker(current_user=admin_user)
        assert result == admin_user


# ── Refresh Token ──


class TestRefreshToken:
    def test_create_and_decode_refresh(self):
        from app.core.security import create_refresh_token, decode_access_token

        token = create_refresh_token(
            data={"sub": "42"},
            secret_key=SECRET,
        )
        payload = decode_access_token(token, secret_key=SECRET)
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"

    def test_access_token_has_type(self):
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token(
            data={"sub": "1", "role": "ADMIN"},
            secret_key=SECRET,
        )
        payload = decode_access_token(token, secret_key=SECRET)
        assert payload["type"] == "access"


# ── User Repository Extensions ──


class TestUserRepositoryExtensions:
    @pytest.mark.asyncio
    async def test_count_empty(self, db_session):
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        assert await repo.count() == 0

    @pytest.mark.asyncio
    async def test_count_with_users(self, db_session, admin_user, regular_user):
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        assert await repo.count() == 2

    @pytest.mark.asyncio
    async def test_get_all_users(self, db_session, admin_user, regular_user):
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        users = await repo.get_all_users()
        assert len(users) == 2
