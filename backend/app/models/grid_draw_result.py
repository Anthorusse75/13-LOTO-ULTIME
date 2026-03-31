"""GridDrawResult model — stores the result of checking played grids against draws."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GridDrawResult(Base):
    __tablename__ = "grid_draw_results"
    __table_args__ = (
        Index("ix_grid_draw_results_grid", "scored_grid_id"),
        Index("ix_grid_draw_results_draw", "draw_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    scored_grid_id: Mapped[int] = mapped_column(
        ForeignKey("scored_grids.id", ondelete="CASCADE"), nullable=False
    )
    draw_id: Mapped[int] = mapped_column(ForeignKey("draws.id", ondelete="CASCADE"), nullable=False)
    matched_numbers: Mapped[list[int]] = mapped_column(JSON, default=list)
    matched_stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    match_count: Mapped[int] = mapped_column(Integer, default=0)
    star_match_count: Mapped[int] = mapped_column(Integer, default=0)
    prize_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_prize: Mapped[float] = mapped_column(Float, default=0.0)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<GridDrawResult(grid={self.scored_grid_id}, draw={self.draw_id}, "
            f"matched={self.match_count}+{self.star_match_count})>"
        )
