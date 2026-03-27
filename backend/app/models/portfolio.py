from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    strategy: Mapped[str] = mapped_column(String(50))
    grid_count: Mapped[int] = mapped_column(Integer)
    grids: Mapped[list[dict]] = mapped_column(JSON)
    diversity_score: Mapped[float] = mapped_column(Float)
    coverage_score: Mapped[float] = mapped_column(Float)
    avg_grid_score: Mapped[float] = mapped_column(Float)
    min_hamming_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<Portfolio(name={self.name!r}, grids={self.grid_count})>"
