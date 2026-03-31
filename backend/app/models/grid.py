from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ScoredGrid(Base):
    __tablename__ = "scored_grids"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    numbers: Mapped[list[int]] = mapped_column(JSON)
    stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)

    total_score: Mapped[float] = mapped_column(Float, index=True)
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    method: Mapped[str] = mapped_column(String(50))
    computed_at: Mapped[datetime] = mapped_column(DateTime)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_played: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    played_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    simulation_stats: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<ScoredGrid(numbers={self.numbers}, score={self.total_score:.2f})>"
