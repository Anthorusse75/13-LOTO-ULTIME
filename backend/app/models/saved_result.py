"""UserSavedResult model — user's saved results history."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserSavedResult(Base):
    __tablename__ = "user_saved_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_definitions.id"), nullable=True, index=True
    )
    result_type: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<UserSavedResult(id={self.id}, type={self.result_type!r})>"
