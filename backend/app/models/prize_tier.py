"""GamePrizeTier model — prize structure per game rank."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GamePrizeTier(Base):
    __tablename__ = "game_prize_tiers"
    __table_args__ = (UniqueConstraint("game_id", "rank", name="uq_prize_tier_game_rank"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    match_numbers: Mapped[int] = mapped_column(Integer, nullable=False)
    match_stars: Mapped[int] = mapped_column(Integer, default=0)
    avg_prize: Mapped[float] = mapped_column(Float, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
