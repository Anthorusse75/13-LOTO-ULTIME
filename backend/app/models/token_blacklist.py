from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TokenBlacklistEntry(Base):
    """Revoked JWT tokens — persisted in DB instead of in-memory."""

    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[float] = mapped_column(Float)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
