from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StatisticsSnapshot(Base):
    __tablename__ = "statistics_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    draw_count: Mapped[int] = mapped_column(Integer)

    # Données statistiques (JSON)
    frequencies: Mapped[dict[str, Any]] = mapped_column(JSON)
    gaps: Mapped[dict[str, Any]] = mapped_column(JSON)
    cooccurrence_matrix: Mapped[dict[str, Any]] = mapped_column(JSON)
    temporal_trends: Mapped[dict[str, Any]] = mapped_column(JSON)
    bayesian_priors: Mapped[dict[str, Any]] = mapped_column(JSON)
    graph_metrics: Mapped[dict[str, Any]] = mapped_column(JSON)
    distribution_stats: Mapped[dict[str, Any]] = mapped_column(JSON)

    # Star/complementary number statistics (nullable — only for games with stars)
    star_frequencies: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )
    star_gaps: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<StatisticsSnapshot(game_id={self.game_id}, at={self.computed_at})>"
