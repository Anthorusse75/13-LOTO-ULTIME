import asyncio
import json
import os
from collections.abc import AsyncGenerator
from datetime import date
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.cache import game_defs_cache, stats_cache

from app.models.base import Base
from app.models.draw import Draw
from app.models.game import GameDefinition
from app.models.grid import ScoredGrid  # noqa: F401
from app.models.job import JobExecution  # noqa: F401
from app.models.portfolio import Portfolio  # noqa: F401
from app.models.prize_tier import GamePrizeTier  # noqa: F401
from app.models.saved_result import UserSavedResult  # noqa: F401
from app.models.statistics import StatisticsSnapshot  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.wheeling import WheelingSystem  # noqa: F401
from app.models.budget import BudgetPlan  # noqa: F401

# ── Env vars required by Settings (no hardcoded defaults) ──
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-min-32-chars!!")
os.environ.setdefault("ADMIN_INITIAL_PASSWORD", "TestAdmin1!")

# ── In-memory SQLite for tests ──
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
def _clear_caches():
    """Clear TTL caches before each test to prevent cross-test pollution."""
    stats_cache.clear()
    game_defs_cache.clear()
    yield
    stats_cache.clear()
    game_defs_cache.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create a test engine (session-scoped)."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional session for each test (rolled back after)."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session, session.begin():
        yield session
        await session.rollback()


@pytest.fixture
async def sample_game(db_session: AsyncSession) -> GameDefinition:
    """Create a sample Loto FDJ game definition."""
    game = GameDefinition(
        name="Loto FDJ",
        slug="loto-fdj",
        numbers_pool=49,
        numbers_drawn=5,
        min_number=1,
        max_number=49,
        stars_pool=10,
        stars_drawn=1,
        star_name="numéro chance",
        draw_frequency="lun/mer/sam",
        historical_source="fdj",
        description="Loto Français - Test",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)
    return game


@pytest.fixture
async def sample_euromillions(db_session: AsyncSession) -> GameDefinition:
    """Create a sample EuroMillions game definition."""
    game = GameDefinition(
        name="EuroMillions",
        slug="euromillions",
        numbers_pool=50,
        numbers_drawn=5,
        min_number=1,
        max_number=50,
        stars_pool=12,
        stars_drawn=2,
        star_name="étoile",
        draw_frequency="mar/ven",
        historical_source="euromillions",
        description="EuroMillions - Test",
        is_active=True,
    )
    db_session.add(game)
    await db_session.flush()
    await db_session.refresh(game)
    return game


@pytest.fixture
async def sample_draws(db_session: AsyncSession, sample_game: GameDefinition) -> list[Draw]:
    """Create 10 sample draws for Loto FDJ."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_draws.json"
    data = json.loads(fixtures_path.read_text(encoding="utf-8"))
    loto_data = next(d for d in data if d["game_slug"] == "loto-fdj")

    draws = []
    for d in loto_data["draws"]:
        draw = Draw(
            game_id=sample_game.id,
            draw_date=date.fromisoformat(d["draw_date"]),
            draw_number=d["draw_number"],
            numbers=d["numbers"],
            stars=d["stars"],
        )
        db_session.add(draw)
        draws.append(draw)

    await db_session.flush()
    for draw in draws:
        await db_session.refresh(draw)
    return draws


@pytest.fixture
async def app_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client for integration tests against the FastAPI app."""
    import os

    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

    from app.main import create_app

    test_app = create_app()
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
