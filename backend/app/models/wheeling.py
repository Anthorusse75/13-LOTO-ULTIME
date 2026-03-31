"""WheelingSystem model — persisted wheeling configurations and results."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WheelingSystem(Base):
    __tablename__ = "wheeling_systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    selected_numbers: Mapped[list[int]] = mapped_column(JSON)
    selected_stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    guarantee_level: Mapped[int] = mapped_column(Integer, nullable=False)
    grids: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    grid_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    coverage_rate: Mapped[float] = mapped_column(Float, nullable=False)
    reduction_rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<WheelingSystem(id={self.id}, game_id={self.game_id}, "
            f"grids={self.grid_count}, t={self.guarantee_level})>"
        )
