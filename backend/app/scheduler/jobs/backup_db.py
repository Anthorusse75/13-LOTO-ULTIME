"""Job: weekly database backup to a timestamped copy."""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from app.core.config import get_settings
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def backup_db_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: create a timestamped backup of the database."""
    await execute_with_tracking(
        job_name="backup_db",
        func=_do_backup,
        triggered_by=triggered_by,
    )


async def _do_backup() -> dict[str, Any]:
    """Backup the database — SQLite file copy or PostgreSQL pg_dump."""
    settings = get_settings()
    db_url = settings.DATABASE_URL

    if db_url.startswith("sqlite"):
        return await _backup_sqlite(db_url)
    elif "postgresql" in db_url or "postgres" in db_url:
        return await _backup_postgresql(db_url)
    else:
        return {"status": "skipped", "reason": f"unsupported database: {db_url.split('://')[0]}"}


async def _backup_sqlite(db_url: str) -> dict[str, Any]:
    """Copy the SQLite database file to a timestamped backup."""
    if ":///" in db_url:
        db_path_str = db_url.split(":///", 1)[1]
    else:
        return {"status": "skipped", "reason": "cannot parse sqlite URL"}

    db_path = Path(db_path_str).resolve()
    if not db_path.exists():
        return {"status": "skipped", "reason": "database file not found"}

    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_{timestamp}{db_path.suffix}"

    shutil.copy2(str(db_path), str(backup_path))
    size_mb = backup_path.stat().st_size / (1024 * 1024)

    logger.info(
        "backup_db.sqlite.done",
        source=str(db_path),
        backup=str(backup_path),
        size_mb=round(size_mb, 2),
    )

    # Keep only the 5 most recent backups
    backups = sorted(backup_dir.glob(f"{db_path.stem}_*{db_path.suffix}"), reverse=True)
    for old in backups[5:]:
        old.unlink()
        logger.info("backup_db.removed_old", path=str(old))

    return {
        "status": "success",
        "type": "sqlite",
        "backup": str(backup_path),
        "size_mb": round(size_mb, 2),
    }


async def _backup_postgresql(db_url: str) -> dict[str, Any]:
    """Dump the PostgreSQL database using pg_dump."""
    # Parse asyncpg URL → psycopg-style for pg_dump
    # postgresql+asyncpg://user:pass@host:port/dbname
    from urllib.parse import urlparse

    parsed = urlparse(db_url.replace("+asyncpg", ""))
    backup_dir = Path("/app/data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dbname = parsed.path.lstrip("/")
    backup_path = backup_dir / f"{dbname}_{timestamp}.sql.gz"

    env = {
        "PGPASSWORD": parsed.password or "",
    }

    cmd = [
        "pg_dump",
        "-h",
        parsed.hostname or "localhost",
        "-p",
        str(parsed.port or 5432),
        "-U",
        parsed.username or "loto",
        "-d",
        dbname,
        "--no-owner",
        "--no-privileges",
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**__import__("os").environ, **env},
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        error_msg = stderr.decode().strip()
        logger.error("backup_db.pg_dump.failed", error=error_msg)
        return {"status": "failed", "error": error_msg}

    import gzip

    with gzip.open(str(backup_path), "wb") as f:
        f.write(stdout)

    size_mb = backup_path.stat().st_size / (1024 * 1024)

    logger.info(
        "backup_db.postgresql.done",
        backup=str(backup_path),
        size_mb=round(size_mb, 2),
    )

    # Keep only the 5 most recent backups
    backups = sorted(backup_dir.glob(f"{dbname}_*.sql.gz"), reverse=True)
    for old in backups[5:]:
        old.unlink()
        logger.info("backup_db.removed_old", path=str(old))

    return {
        "status": "success",
        "type": "postgresql",
        "backup": str(backup_path),
        "size_mb": round(size_mb, 2),
    }

    return {
        "status": "success",
        "backup_path": str(backup_path),
        "size_mb": round(size_mb, 2),
    }
