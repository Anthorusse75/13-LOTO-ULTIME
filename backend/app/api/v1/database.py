"""Database admin API — info, connection details, and engine switch."""

import os
from urllib.parse import urlparse

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.dependencies import get_db, require_role
from app.models.draw import Draw
from app.models.game import GameDefinition
from app.models.user import User, UserRole

router = APIRouter(dependencies=[Depends(require_role(UserRole.ADMIN))])
logger = structlog.get_logger(__name__)


def _parse_db_info(database_url: str) -> dict:
    """Extract connection details from a DATABASE_URL."""
    if database_url.startswith("sqlite"):
        path = database_url.split(":///", 1)[1] if ":///" in database_url else "unknown"
        return {
            "engine": "sqlite",
            "driver": "aiosqlite",
            "host": None,
            "port": None,
            "database": path,
            "user": None,
            "password": None,
            "connections": None,
        }

    parsed = urlparse(database_url.replace("+asyncpg", "").replace("+psycopg2", ""))
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    db = (parsed.path or "/").lstrip("/")
    user = parsed.username or "loto"
    password = parsed.password or ""
    masked_password = "***" if password else ""

    # External host comes from env or defaults to the Docker host IP
    ext_host = os.environ.get("SERVER_IP", "192.168.0.94")
    ext_port = os.environ.get("POSTGRES_PORT", str(port))

    return {
        "engine": "postgresql",
        "driver": "asyncpg",
        "host": host,
        "port": port,
        "database": db,
        "user": user,
        "password": masked_password,
        "connections": {
            "internal": {
                "label": "Même docker-compose",
                "host": host,
                "port": port,
                "url": f"postgresql://{user}:****@{host}:{port}/{db}",
            },
            "docker_network": {
                "label": "Autre Docker (réseau shared-db)",
                "host": "loto-ultime-postgres",
                "port": 5432,
                "url": f"postgresql://{user}:****@loto-ultime-postgres:5432/{db}",
                "network": "shared-db",
            },
            "external": {
                "label": "Externe (réseau local)",
                "host": ext_host,
                "port": int(ext_port),
                "url": f"postgresql://{user}:****@{ext_host}:{ext_port}/{db}",
            },
        },
    }


@router.get("")
async def get_database_info(session: AsyncSession = Depends(get_db)):
    """Return current database engine info, stats, and connection details."""
    settings = get_settings()
    info = _parse_db_info(settings.DATABASE_URL)

    # Count rows in key tables
    draws_count = (await session.execute(select(func.count(Draw.id)))).scalar() or 0
    games_count = (await session.execute(select(func.count(GameDefinition.id)))).scalar() or 0
    users_count = (await session.execute(select(func.count(User.id)))).scalar() or 0

    # Get DB version
    try:
        if info["engine"] == "postgresql":
            version = (await session.execute(text("SELECT version()"))).scalar()
        else:
            version = (await session.execute(text("SELECT sqlite_version()"))).scalar()
    except Exception:
        version = "unknown"

    return {
        **info,
        "version": version,
        "stats": {
            "draws": draws_count,
            "games": games_count,
            "users": users_count,
        },
    }


@router.post("/switch")
async def switch_database(
    payload: dict,
    session: AsyncSession = Depends(get_db),
):
    """Switch the database engine. Expects { "engine": "postgresql" | "sqlite" }.

    - Closes the current engine
    - Connects to the new database
    - Runs Alembic migrations (creates schema if needed)
    - Seeds games + admin
    - If no draws exist, triggers initial data fetch
    """
    engine_type = payload.get("engine")
    if engine_type not in ("sqlite", "postgresql"):
        raise HTTPException(status_code=422, detail="engine must be 'sqlite' or 'postgresql'")

    settings = get_settings()
    current_info = _parse_db_info(settings.DATABASE_URL)

    if current_info["engine"] == engine_type:
        raise HTTPException(status_code=409, detail=f"Already using {engine_type}")

    # Build the new DATABASE_URL
    if engine_type == "postgresql":
        # Use env vars for PostgreSQL credentials (same as docker-compose)
        import os

        pg_user = os.environ.get("POSTGRES_USER", "loto")
        pg_pass = os.environ.get("POSTGRES_PASSWORD", "")
        if not pg_pass:
            raise HTTPException(status_code=400, detail="POSTGRES_PASSWORD env var is not set")
        pg_host = os.environ.get("POSTGRES_HOST", "postgres")
        pg_port = os.environ.get("POSTGRES_PORT", "5432")
        pg_db = os.environ.get("POSTGRES_DB", "loto_ultime")
        new_url = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    else:
        new_url = "sqlite+aiosqlite:////app/data/loto_ultime.db"

    logger.info("database.switching", from_engine=current_info["engine"], to_engine=engine_type)

    # 1. Close current engine
    from app.models.base import close_db, init_db

    await close_db()

    # 2. Init new engine
    init_db(new_url)

    # 3. Run Alembic migrations on the new database
    import os
    import subprocess

    env = {**os.environ, "DATABASE_URL": new_url}
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            timeout=30,
        )
        if result.returncode != 0:
            logger.error("database.migration_failed", stderr=result.stderr)
            # Rollback to previous engine
            init_db(settings.DATABASE_URL)
            raise HTTPException(
                status_code=500,
                detail=f"Migration failed: {result.stderr[:200]}",
            )
    except subprocess.TimeoutExpired as exc:
        init_db(settings.DATABASE_URL)
        raise HTTPException(status_code=500, detail="Migration timed out") from exc

    # 4. Update settings in memory
    settings.DATABASE_URL = new_url

    # 5. Seed games + admin
    from app.main import _seed_admin, _seed_games

    await _seed_games()
    await _seed_admin()

    # 6. Check if draws exist — if not, trigger fetch
    from app.models.base import get_session

    async for new_session in get_session():
        count = (await new_session.execute(select(func.count(Draw.id)))).scalar() or 0
        break

    fetch_triggered = False
    if count == 0:
        from app.main import _maybe_initial_fetch

        await _maybe_initial_fetch()
        fetch_triggered = True

    new_info = _parse_db_info(new_url)

    logger.info(
        "database.switched",
        engine=engine_type,
        draws=count,
        fetch_triggered=fetch_triggered,
    )

    return {
        **new_info,
        "status": "switched",
        "draws_found": count,
        "fetch_triggered": fetch_triggered,
    }
