"""Tests for core configuration."""

from pathlib import Path

import pytest


class TestSettings:
    def test_settings_from_env(self, monkeypatch):
        """Settings should load from environment variables."""
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-at-least-32-characters-long")
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
        monkeypatch.setenv("DEBUG", "true")

        from app.core.config import Settings

        settings = Settings()
        assert settings.SECRET_KEY == "test-secret-key-at-least-32-characters-long"
        assert settings.DEBUG is True
        assert "test.db" in settings.DATABASE_URL

    def test_settings_defaults(self, monkeypatch):
        """Settings should have proper defaults."""
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-at-least-32-characters-long")

        from app.core.config import Settings

        settings = Settings()
        assert settings.APP_NAME == "LOTO ULTIME"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRATION_MINUTES == 60
        assert settings.RATE_LIMIT_PER_MINUTE == 60

    def test_settings_secret_key_required(self, monkeypatch):
        """Settings should fail without SECRET_KEY."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        # Remove .env loading
        monkeypatch.setattr(
            "pydantic_settings.BaseSettings.model_config",
            {
                "env_file": "/nonexistent/.env",
                "case_sensitive": True,
            },
        )

        from app.core.config import Settings

        with pytest.raises(Exception):  # noqa: B017
            Settings(_env_file="/nonexistent/.env")


class TestGameDefinitions:
    def test_load_game_config(self, tmp_path: Path):
        """Should load a YAML game config."""
        yaml_content = """
name: "Test Game"
slug: "test-game"
numbers_pool: 49
numbers_drawn: 5
min_number: 1
max_number: 49
"""
        config_file = tmp_path / "test.yaml"
        config_file.write_text(yaml_content, encoding="utf-8")

        from app.core.game_definitions import load_game_config

        config = load_game_config(config_file)
        assert config.name == "Test Game"
        assert config.slug == "test-game"
        assert config.numbers_pool == 49
        assert config.numbers_drawn == 5
        assert config.stars_pool is None

    def test_load_all_game_configs(self):
        """Should load all YAML configs from game_configs dir."""
        from app.core.game_definitions import load_all_game_configs

        config_dir = Path(__file__).resolve().parent.parent.parent / "game_configs"
        configs = load_all_game_configs(config_dir)

        assert "loto-fdj" in configs
        assert "euromillions" in configs
        assert configs["loto-fdj"].numbers_pool == 49
        assert configs["euromillions"].stars_drawn == 2

    def test_game_config_immutable(self, tmp_path: Path):
        """GameConfig should be frozen (immutable)."""
        yaml_content = """
name: "Test"
slug: "test"
numbers_pool: 49
numbers_drawn: 5
min_number: 1
max_number: 49
"""
        config_file = tmp_path / "test.yaml"
        config_file.write_text(yaml_content, encoding="utf-8")

        from app.core.game_definitions import load_game_config

        config = load_game_config(config_file)
        with pytest.raises(AttributeError):
            config.name = "Modified"
