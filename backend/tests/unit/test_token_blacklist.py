"""Tests for the DB-backed token blacklist module."""

import time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.token_blacklist import TokenBlacklist
from app.models.base import Base


@pytest.fixture
async def bl_session():
    """Create an in-memory SQLite session for blacklist tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def test_blacklist_initially_empty(bl_session: AsyncSession):
    bl = TokenBlacklist(bl_session)
    assert not await bl.is_revoked("abc")


async def test_revoke_marks_as_revoked(bl_session: AsyncSession):
    bl = TokenBlacklist(bl_session)
    await bl.revoke("jti-1", time.time() + 3600)
    assert await bl.is_revoked("jti-1")
    assert not await bl.is_revoked("jti-2")


async def test_cleanup_removes_expired(bl_session: AsyncSession):
    bl = TokenBlacklist(bl_session)
    await bl.revoke("old", time.time() - 10)
    await bl.revoke("new", time.time() + 3600)
    await bl.cleanup()
    assert not await bl.is_revoked("old")
    assert await bl.is_revoked("new")


def test_jti_in_access_token():
    from app.core.security import create_access_token, decode_access_token

    token = create_access_token(data={"sub": "1"}, secret_key="test-secret", expires_minutes=60)
    payload = decode_access_token(token, "test-secret")
    assert "jti" in payload
    assert len(payload["jti"]) == 32  # hex uuid4


def test_jti_in_refresh_token():
    from app.core.security import create_refresh_token, decode_access_token

    token = create_refresh_token(data={"sub": "1"}, secret_key="test-secret", expires_days=7)
    payload = decode_access_token(token, "test-secret")
    assert "jti" in payload
    assert payload["type"] == "refresh"
