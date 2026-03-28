"""Tests for the token blacklist module."""

import time

from app.core.token_blacklist import TokenBlacklist, get_token_blacklist


def test_blacklist_initially_empty():
    bl = TokenBlacklist()
    assert not bl.is_revoked("abc")


def test_revoke_marks_as_revoked():
    bl = TokenBlacklist()
    bl.revoke("jti-1", time.time() + 3600)
    assert bl.is_revoked("jti-1")
    assert not bl.is_revoked("jti-2")


def test_cleanup_removes_expired():
    bl = TokenBlacklist()
    bl.revoke("old", time.time() - 10)
    bl.revoke("new", time.time() + 3600)
    bl.cleanup()
    assert not bl.is_revoked("old")
    assert bl.is_revoked("new")


def test_singleton_instance():
    bl1 = get_token_blacklist()
    bl2 = get_token_blacklist()
    assert bl1 is bl2


def test_jti_in_access_token():
    from app.core.security import create_access_token, decode_access_token

    token = create_access_token(
        data={"sub": "1"}, secret_key="test-secret", expires_minutes=60
    )
    payload = decode_access_token(token, "test-secret")
    assert "jti" in payload
    assert len(payload["jti"]) == 32  # hex uuid4


def test_jti_in_refresh_token():
    from app.core.security import create_refresh_token, decode_access_token

    token = create_refresh_token(
        data={"sub": "1"}, secret_key="test-secret", expires_days=7
    )
    payload = decode_access_token(token, "test-secret")
    assert "jti" in payload
    assert payload["type"] == "refresh"
