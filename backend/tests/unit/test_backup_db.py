"""Unit tests for backup_db job."""

from pathlib import Path
from unittest.mock import patch

import pytest


class TestBackupDb:
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temp database file."""
        db_file = tmp_path / "loto_ultime.db"
        db_file.write_text("fake database content")
        return db_file

    @pytest.mark.asyncio
    async def test_do_backup_creates_file(self, temp_db):
        from app.scheduler.jobs.backup_db import _do_backup

        with patch("app.scheduler.jobs.backup_db.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = f"sqlite+aiosqlite:///{temp_db}"
            result = await _do_backup()

        assert result["status"] == "success"
        assert "backup_path" in result
        backup = Path(result["backup_path"])
        assert backup.exists()

    @pytest.mark.asyncio
    async def test_do_backup_keeps_max_5(self, temp_db):
        from app.scheduler.jobs.backup_db import _do_backup

        with patch("app.scheduler.jobs.backup_db.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = f"sqlite+aiosqlite:///{temp_db}"
            # Create 7 backups
            for _ in range(7):
                await _do_backup()

        backup_dir = temp_db.parent / "backups"
        backups = list(backup_dir.glob("loto_ultime_*.db"))
        assert len(backups) <= 5

    @pytest.mark.asyncio
    async def test_do_backup_skips_non_sqlite(self):
        from app.scheduler.jobs.backup_db import _do_backup

        with patch("app.scheduler.jobs.backup_db.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = "postgresql://localhost/test"
            result = await _do_backup()

        assert result["status"] == "skipped"
