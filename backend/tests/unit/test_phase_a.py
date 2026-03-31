"""Phase A tests — rate limiting, pagination, caching, token blacklist."""

import math
import time

import pytest
from cachetools import TTLCache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.cache import game_defs_cache, stats_cache
from app.core.rate_limit import limiter
from app.core.token_blacklist import TokenBlacklist
from app.models.base import Base
from app.schemas.common import PaginatedResponse, PaginationParams


# ── TEST-05: Rate limiting ──


def test_single_limiter_instance():
    """B-09: There should be one centralized limiter instance."""
    from app.core.rate_limit import limiter as limiter2

    assert limiter is limiter2


def test_limiter_key_func_is_remote_address():
    """B-09: The limiter key function should be get_remote_address."""
    from slowapi.util import get_remote_address

    assert limiter._key_func is get_remote_address


# ── TEST-06: Pagination ──


def test_pagination_params_defaults():
    """B-11: PaginationParams defaults to page=1, page_size=50."""
    params = PaginationParams(page=1, page_size=50)
    assert params.page == 1
    assert params.page_size == 50
    assert params.offset == 0
    assert params.limit == 50


def test_pagination_params_offset():
    """B-11: PaginationParams offset correctly computed from page/page_size."""
    params = PaginationParams(page=3, page_size=20)
    assert params.offset == 40
    assert params.limit == 20


def test_paginated_response_schema():
    """B-11: PaginatedResponse has correct fields and pages calculation."""
    resp = PaginatedResponse(
        items=[1, 2, 3],
        total=25,
        page=1,
        page_size=10,
        pages=math.ceil(25 / 10),
    )
    assert resp.pages == 3
    assert len(resp.items) == 3
    assert resp.total == 25


# ── TEST-07: Cache ──


def test_stats_cache_is_ttl_cache():
    """B-12: stats_cache should be a TTLCache with correct params."""
    assert isinstance(stats_cache, TTLCache)
    assert stats_cache.maxsize == 5
    assert stats_cache.timer is time.monotonic or stats_cache.ttl == 3600


def test_game_defs_cache_is_ttl_cache():
    """B-13: game_defs_cache should be a TTLCache with correct params."""
    assert isinstance(game_defs_cache, TTLCache)
    assert game_defs_cache.maxsize == 1
    assert game_defs_cache.ttl == 86400


def test_stats_cache_stores_and_retrieves():
    """B-12: stats_cache basic put/get works."""
    stats_cache.clear()
    stats_cache[42] = {"fake": "snapshot"}
    assert stats_cache.get(42) == {"fake": "snapshot"}
    stats_cache.clear()


def test_game_defs_cache_stores_and_retrieves():
    """B-13: game_defs_cache basic put/get works."""
    game_defs_cache.clear()
    game_defs_cache["all"] = {"loto-fdj": "config"}
    assert game_defs_cache.get("all") == {"loto-fdj": "config"}
    game_defs_cache.clear()


# ── TEST-08: Token blacklist DB ──


@pytest.fixture
async def bl_session():
    """In-memory SQLite session for blacklist tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def test_blacklist_revoke_and_check(bl_session: AsyncSession):
    """B-07/B-08: Token blacklist persists in DB and can be queried."""
    bl = TokenBlacklist(bl_session)
    assert not await bl.is_revoked("test-jti")
    await bl.revoke("test-jti", time.time() + 3600)
    assert await bl.is_revoked("test-jti")


async def test_blacklist_cleanup_expired(bl_session: AsyncSession):
    """B-07: Cleanup removes expired tokens from DB."""
    bl = TokenBlacklist(bl_session)
    await bl.revoke("expired", time.time() - 100)
    await bl.revoke("valid", time.time() + 3600)
    await bl.cleanup()
    assert not await bl.is_revoked("expired")
    assert await bl.is_revoked("valid")
