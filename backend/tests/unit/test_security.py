"""Tests for security utilities."""

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("MySecurePassword123!")
        assert hashed != "MySecurePassword123!"
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        hashed = hash_password("TestPass")
        assert verify_password("TestPass", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("TestPass")
        assert verify_password("WrongPass", hashed) is False


class TestJWT:
    SECRET = "test-secret-key-for-jwt-testing-32chars!!"

    def test_create_and_decode_token(self):
        token = create_access_token(data={"sub": "testuser"}, secret_key=self.SECRET)
        payload = decode_access_token(token, secret_key=self.SECRET)
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        from jose import JWTError

        with pytest.raises(JWTError):
            decode_access_token("invalid.token.here", secret_key=self.SECRET)

    def test_decode_wrong_secret(self):
        from jose import JWTError

        token = create_access_token(data={"sub": "user"}, secret_key=self.SECRET)
        with pytest.raises(JWTError):
            decode_access_token(token, secret_key="wrong-secret-key-that-is-different!!")
