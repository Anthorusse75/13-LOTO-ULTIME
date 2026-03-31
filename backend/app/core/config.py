from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration applicative — chargée depuis .env et variables d'environnement."""

    # Application
    APP_NAME: str = "LOTO ULTIME"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Base de données (SQLite pour dev local, PostgreSQL pour Docker/prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./loto_ultime.db"

    # Sécurité — HS256 (symétrique, défaut)
    SECRET_KEY: str = Field(..., min_length=32)
    PREVIOUS_SECRET_KEY: str | None = Field(None)  # Pour la rotation gracieuse du secret JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Sécurité — RS256 (asymétrique, multi-service)
    # Fournissez le contenu PEM ou le chemin vers les fichiers.
    # Si JWT_ALGORITHM=RS256, ces deux variables sont obligatoires.
    JWT_PRIVATE_KEY: str | None = None  # Contenu PEM de la clé privée RSA
    JWT_PUBLIC_KEY: str | None = None  # Contenu PEM de la clé publique RSA
    JWT_PRIVATE_KEY_PATH: str | None = None  # Chemin fichier alternative
    JWT_PUBLIC_KEY_PATH: str | None = None  # Chemin fichier alternative

    # Admin initial
    ADMIN_EMAIL: str = "admin@loto-ultime.local"
    ADMIN_INITIAL_PASSWORD: str = Field(..., min_length=8)

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

    # LLM — Groq (gratuit, optionnel)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = {
        "env_file": Path(__file__).resolve().parents[2] / ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _resolve_rsa_keys(self) -> "Settings":
        """Load RSA key PEM content from files if paths provided, and validate RS256 config."""
        if self.JWT_ALGORITHM == "RS256":
            # Try to load from path if content not set directly
            if not self.JWT_PRIVATE_KEY and self.JWT_PRIVATE_KEY_PATH:
                self.JWT_PRIVATE_KEY = Path(self.JWT_PRIVATE_KEY_PATH).read_text()
            if not self.JWT_PUBLIC_KEY and self.JWT_PUBLIC_KEY_PATH:
                self.JWT_PUBLIC_KEY = Path(self.JWT_PUBLIC_KEY_PATH).read_text()

            if not self.JWT_PRIVATE_KEY or not self.JWT_PUBLIC_KEY:
                raise ValueError(
                    "JWT_ALGORITHM=RS256 requires JWT_PRIVATE_KEY and JWT_PUBLIC_KEY "
                    "(or corresponding _PATH variants) to be set."
                )
        return self

    def get_jwt_signing_key(self) -> str:
        """Return the appropriate signing key for JWT creation."""
        if self.JWT_ALGORITHM == "RS256":
            return self.JWT_PRIVATE_KEY  # type: ignore[return-value]
        return self.SECRET_KEY

    def get_jwt_verify_key(self) -> str:
        """Return the appropriate verification key for JWT decoding."""
        if self.JWT_ALGORITHM == "RS256":
            return self.JWT_PUBLIC_KEY  # type: ignore[return-value]
        return self.SECRET_KEY


def get_settings() -> Settings:
    """Factory pour la configuration (cacheable via lru_cache si nécessaire)."""
    return Settings()
