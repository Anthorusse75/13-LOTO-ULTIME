"""Job: weekly database backup to a timestamped copy."""

import shutil
from datetime import datetime
from pathlib import Path

import structlog

from app.core.config import get_settings
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def backup_db_job(triggered_by: str = "scheduler") -> None:
    """Scheduled job: create a timestamped backup of the SQLite database."""
    await execute_with_tracking(
        job_name="backup_db",
        func=_do_backup,
        triggered_by=triggered_by,
    )


async def _do_backup() -> dict:
    """Copy the database file to a timestamped backup."""
    settings = get_settings()
    db_url = settings.DATABASE_URL

    # Extract path from sqlite URL (sqlite+aiosqlite:///./loto_ultime.db)
    if ":///" in db_url:
        db_path_str = db_url.split(":///", 1)[1]
    else:
        return {"status": "skipped", "reason": "non-sqlite database"}

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
        "backup_db.done",
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
        "backup_path": str(backup_path),
        "size_mb": round(size_mb, 2),
    }
