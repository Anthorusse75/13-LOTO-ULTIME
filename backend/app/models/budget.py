"""BudgetPlan model — persisted budget optimization results."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class BudgetPlan(Base):
    __tablename__ = "budget_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    objective: Mapped[str] = mapped_column(String(20), nullable=False)
    selected_numbers: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    chosen_strategy: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<BudgetPlan(id={self.id}, budget={self.budget}, obj={self.objective})>"
