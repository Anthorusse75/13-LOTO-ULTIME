from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration applicative — chargée depuis .env et variables d'environnement."""

    # Application
    APP_NAME: str = "LOTO ULTIME"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Base de données
    DATABASE_URL: str = "sqlite+aiosqlite:///./loto_ultime.db"

    # Sécurité
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Admin initial
    ADMIN_EMAIL: str = "admin@loto-ultime.local"
    ADMIN_INITIAL_PASSWORD: str = "ChangeMe123!"

    # Scheduler
    SCHEDULER_ENABLED: bool = False

    # Scraper
    FDJ_BASE_URL: str = "https://www.fdj.fr"
    EUROMILLIONS_BASE_URL: str = "https://www.fdj.fr"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.0.124:5173",
    ]

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    model_config = {
        "env_file": Path(__file__).resolve().parents[2] / ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Factory pour la configuration (cacheable via lru_cache si nécessaire)."""
    return Settings()
