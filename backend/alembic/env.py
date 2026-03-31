import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.models.base import Base
from app.models.draw import Draw  # noqa: F401

# Import all models so Alembic can detect them
from app.models.game import GameDefinition  # noqa: F401
from app.models.grid import ScoredGrid  # noqa: F401
from app.models.job import JobExecution  # noqa: F401
from app.models.portfolio import Portfolio  # noqa: F401
from app.models.statistics import StatisticsSnapshot  # noqa: F401
from app.models.user import User  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

    engine_kwargs: dict = {"poolclass": pool.NullPool}
    if url and url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    connectable = create_async_engine(url, **engine_kwargs)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
