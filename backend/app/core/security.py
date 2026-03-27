from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(
    data: dict, secret_key: str, algorithm: str = "HS256", expires_minutes: int = 60
) -> str:
    """Crée un token JWT signé."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict:
    """Décode et valide un token JWT. Lève JWTError si invalide."""
    return jwt.decode(token, secret_key, algorithms=[algorithm])
