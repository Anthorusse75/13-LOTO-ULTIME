import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import jwt


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(
    data: dict[str, Any], secret_key: str, algorithm: str = "HS256", expires_minutes: int = 60
) -> str:
    """Crée un token JWT signé avec un JTI unique.

    Pour RS256, `secret_key` doit contenir le contenu PEM de la clé privée RSA.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "type": "access", "jti": uuid.uuid4().hex})
    return str(jwt.encode(to_encode, secret_key, algorithm=algorithm))


def create_refresh_token(
    data: dict[str, Any], secret_key: str, algorithm: str = "HS256", expires_days: int = 7
) -> str:
    """Crée un refresh token JWT signé avec un JTI unique.

    Pour RS256, `secret_key` doit contenir le contenu PEM de la clé privée RSA.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=expires_days)
    to_encode.update({"exp": expire, "type": "refresh", "jti": uuid.uuid4().hex})
    return str(jwt.encode(to_encode, secret_key, algorithm=algorithm))


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
    previous_secret_key: str | None = None,
) -> dict[str, Any]:
    """Décode et valide un token JWT.

    Pour RS256 : `secret_key` doit contenir le contenu PEM de la clé *publique*.
    Les algorithmes asymétriques (RS256) ne nécessitent pas de previous_secret_key
    car la rotation se fait par rotation de clé publique.
    """
    try:
        return dict(jwt.decode(token, secret_key, algorithms=[algorithm]))
    except Exception:
        if previous_secret_key and algorithm == "HS256":
            # Rotation gracieuse uniquement pour HS256 (clé symétrique)
            return dict(jwt.decode(token, previous_secret_key, algorithms=[algorithm]))
        raise
