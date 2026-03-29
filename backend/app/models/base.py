from datetime import datetime

from sqlalchemy import event, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_async_engine(database_url, echo=False, connect_args=connect_args)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    # Activate PRAGMA foreign_keys for SQLite connections
    if database_url.startswith("sqlite"):

        @event.listens_for(_engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


async def get_session() -> AsyncSession:
    """Fournit une session async (à utiliser comme dependency FastAPI)."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        yield session  # type: ignore[misc]


async def close_db() -> None:
    """Ferme proprement le moteur de base de données."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_engine():
    """Retourne le moteur SQLAlchemy (pour Alembic notamment)."""
    return _engine
