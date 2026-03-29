"""In-memory token blacklist for invalidated JWTs."""

import threading
import time


class TokenBlacklist:
    """Thread-safe set of revoked JTI (JWT ID) values with auto-expiry cleanup."""

    def __init__(self) -> None:
        self._revoked: dict[str, float] = {}  # jti -> expiry timestamp
        self._lock = threading.Lock()

    def revoke(self, jti: str, exp: float) -> None:
        """Add a token JTI to the blacklist until its natural expiry."""
        with self._lock:
            self._revoked[jti] = exp

    def is_revoked(self, jti: str) -> bool:
        """Check if a JTI has been revoked."""
        with self._lock:
            return jti in self._revoked

    def cleanup(self) -> None:
        """Remove expired entries from the blacklist."""
        now = time.time()
        with self._lock:
            self._revoked = {jti: exp for jti, exp in self._revoked.items() if exp > now}


# Singleton instance
_blacklist = TokenBlacklist()


def get_token_blacklist() -> TokenBlacklist:
    return _blacklist
