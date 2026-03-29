"""Tests: JWT token expiry verification."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.core.security import create_access_token, create_refresh_token, decode_access_token

SECRET = "test-secret-key-minimum-32-chars-long!"
ALGO = "HS256"


class TestJWTExpiry:
    """Verify that JWT tokens expire correctly."""

    def test_access_token_contains_exp_claim(self):
        token = create_access_token(
            data={"sub": "1", "role": "ADMIN"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_minutes=60,
        )
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        assert "exp" in payload
        assert payload["type"] == "access"

    def test_access_token_expires_at_correct_time(self):
        before = datetime.now(UTC)
        token = create_access_token(
            data={"sub": "1"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_minutes=30,
        )
        after = datetime.now(UTC)
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        # exp is an integer timestamp — allow 1s tolerance
        assert before + timedelta(minutes=30) - timedelta(seconds=1) <= exp
        assert exp <= after + timedelta(minutes=30) + timedelta(seconds=1)

    def test_refresh_token_contains_exp_claim(self):
        token = create_refresh_token(
            data={"sub": "1"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_days=7,
        )
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        assert "exp" in payload
        assert payload["type"] == "refresh"

    def test_refresh_token_expires_at_correct_time(self):
        before = datetime.now(UTC)
        token = create_refresh_token(
            data={"sub": "1"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_days=7,
        )
        after = datetime.now(UTC)
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        # exp is an integer timestamp — allow 1s tolerance
        assert before + timedelta(days=7) - timedelta(seconds=1) <= exp
        assert exp <= after + timedelta(days=7) + timedelta(seconds=1)

    def test_expired_access_token_raises(self):
        token = create_access_token(
            data={"sub": "1"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_minutes=-1,  # already expired
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token, SECRET, ALGO)

    def test_decode_access_token_valid(self):
        token = create_access_token(
            data={"sub": "42", "username": "test", "role": "ADMIN"},
            secret_key=SECRET,
            algorithm=ALGO,
            expires_minutes=60,
        )
        payload = decode_access_token(token, SECRET, ALGO)
        assert payload["sub"] == "42"
        assert payload["username"] == "test"
        assert payload["role"] == "ADMIN"

    def test_default_access_expiry_is_60_minutes(self):
        """Config default: JWT_EXPIRATION_MINUTES = 60."""
        # Settings uses env: provide a minimal SECRET_KEY
        import os

        from app.core.config import Settings

        old = os.environ.get("SECRET_KEY")
        os.environ["SECRET_KEY"] = SECRET
        try:
            s = Settings()
            assert s.JWT_EXPIRATION_MINUTES == 60
            assert s.REFRESH_TOKEN_EXPIRE_DAYS == 7
        finally:
            if old is None:
                os.environ.pop("SECRET_KEY", None)
            else:
                os.environ["SECRET_KEY"] = old
