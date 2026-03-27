from datetime import datetime

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
    frequencies: Mapped[dict] = mapped_column(JSON)
    gaps: Mapped[dict] = mapped_column(JSON)
    cooccurrence_matrix: Mapped[dict] = mapped_column(JSON)
    temporal_trends: Mapped[dict] = mapped_column(JSON)
    bayesian_priors: Mapped[dict] = mapped_column(JSON)
    graph_metrics: Mapped[dict] = mapped_column(JSON)
    distribution_stats: Mapped[dict] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<StatisticsSnapshot(game_id={self.game_id}, at={self.computed_at})>"
