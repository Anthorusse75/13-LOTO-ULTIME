from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from sqlalchemy import event, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool, StaticPool


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(default=None, onupdate=func.now())


# ── Engine & Session factory (configurés au démarrage) ──

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str) -> None:
    """Initialise le moteur et la session factory."""
    global _engine, _session_factory

    connect_args: dict[str, Any] = {}
    pool_class = None
    is_sqlite = database_url.startswith("sqlite")

    if is_sqlite:
        connect_args["check_same_thread"] = False
        pool_class = StaticPool if ":memory:" in database_url else NullPool

    engine_kwargs: dict[str, Any] = {
        "echo": False,
    }
    if connect_args:
        engine_kwargs["connect_args"] = connect_args
    if pool_class is not None:
        engine_kwargs["poolclass"] = pool_class
    elif not is_sqlite:
        # PostgreSQL : pool de connexions avec des valeurs raisonnables
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_pre_ping"] = True

    _engine = create_async_engine(database_url, **engine_kwargs)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    # Activate PRAGMA foreign_keys for SQLite connections
    if is_sqlite:

        @event.listens_for(_engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session async (à utiliser comme dependency FastAPI)."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        yield session


async def close_db() -> None:
    """Ferme proprement le moteur de base de données."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_engine() -> Any:
    """Retourne le moteur SQLAlchemy (pour Alembic notamment)."""
    return _engine
