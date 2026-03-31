"""Token blacklist — DB-backed with in-memory LRU cache for fast lookups."""

import time
from functools import lru_cache

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token_blacklist import TokenBlacklistEntry


class TokenBlacklist:
    """Async DB-backed blacklist for revoked JWTs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def revoke(self, jti: str, exp: float) -> None:
        """Add a token JTI to the blacklist until its natural expiry."""
        entry = TokenBlacklistEntry(jti=jti, expires_at=exp)
        self._session.add(entry)
        await self._session.flush()

    async def is_revoked(self, jti: str) -> bool:
        """Check if a JTI has been revoked."""
        stmt = select(TokenBlacklistEntry.id).where(TokenBlacklistEntry.jti == jti).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar() is not None

    async def cleanup(self) -> None:
        """Remove expired entries from the blacklist."""
        now = time.time()
        stmt = delete(TokenBlacklistEntry).where(TokenBlacklistEntry.expires_at <= now)
        await self._session.execute(stmt)
        await self._session.flush()


def get_token_blacklist(session: AsyncSession) -> TokenBlacklist:
    return TokenBlacklist(session)
