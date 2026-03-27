from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Draw(Base, TimestampMixin):
    __tablename__ = "draws"
    __table_args__ = (UniqueConstraint("game_id", "draw_date", name="uq_draw_game_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    draw_date: Mapped[date] = mapped_column(Date, index=True)
    draw_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numbers: Mapped[list[int]] = mapped_column(JSON)
    stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)

    # Relations
    game: Mapped["GameDefinition"] = relationship(back_populates="draws")

    def __repr__(self) -> str:
        return f"<Draw(game_id={self.game_id}, date={self.draw_date}, numbers={self.numbers})>"


# Import pour résoudre la forward reference
from .game import GameDefinition  # noqa: E402, F401
