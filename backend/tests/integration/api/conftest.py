"""Shared fixtures for integration API tests needing authentication."""

from dataclasses import dataclass

import pytest

from app.core.security import create_access_token
from app.models.user import UserRole

TEST_SECRET = "test-secret-key-for-testing-min-32-chars!!"


@dataclass
class FakeUser:
    """Lightweight user stand-in for dependency overrides (no SQLAlchemy state)."""

    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    hashed_password: str = ""
    last_login: object = None


def make_fake_admin() -> FakeUser:
    """Create a fake admin user object for dependency overrides."""
    return FakeUser(
        id=1,
        username="admin",
        email="admin@test.local",
        role=UserRole.ADMIN,
    )


def make_fake_utilisateur() -> FakeUser:
    """Create a fake UTILISATEUR user object for dependency overrides."""
    return FakeUser(
        id=2,
        username="user",
        email="user@test.local",
        role=UserRole.UTILISATEUR,
    )


def override_auth(app, role: str = "ADMIN"):
    """Override get_current_user dependency on a FastAPI app for testing."""
    from app.dependencies import get_current_user

    fake_user = make_fake_admin() if role == "ADMIN" else make_fake_utilisateur()

    async def _fake_current_user():
        return fake_user

    app.dependency_overrides[get_current_user] = _fake_current_user


@pytest.fixture
def admin_auth_header() -> dict[str, str]:
    """Return an Authorization header with a valid ADMIN JWT token."""
    token = create_access_token(
        data={"sub": "1", "username": "admin", "role": "ADMIN"},
        secret_key=TEST_SECRET,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_header() -> dict[str, str]:
    """Return an Authorization header with a valid UTILISATEUR JWT token."""
    token = create_access_token(
        data={"sub": "2", "username": "user", "role": "UTILISATEUR"},
        secret_key=TEST_SECRET,
    )
    return {"Authorization": f"Bearer {token}"}
