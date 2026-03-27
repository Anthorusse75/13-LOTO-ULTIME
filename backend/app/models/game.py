from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class GameDefinition(Base, TimestampMixin):
    __tablename__ = "game_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    numbers_pool: Mapped[int] = mapped_column(Integer)
    numbers_drawn: Mapped[int] = mapped_column(Integer)
    min_number: Mapped[int] = mapped_column(Integer, default=1)
    max_number: Mapped[int] = mapped_column(Integer)
    stars_pool: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stars_drawn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    star_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    draw_frequency: Mapped[str] = mapped_column(String(50))
    historical_source: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relations
    draws: Mapped[list["Draw"]] = relationship(back_populates="game", lazy="selectin")

    def __repr__(self) -> str:
        return f"<GameDefinition(slug={self.slug!r})>"


# Import pour résoudre la forward reference
from .draw import Draw  # noqa: E402, F401
