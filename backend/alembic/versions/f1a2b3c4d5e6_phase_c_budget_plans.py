"""Phase C – budget_plans table

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budget_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "game_id",
            sa.Integer(),
            sa.ForeignKey("game_definitions.id"),
            nullable=False,
        ),
        sa.Column("budget", sa.Float(), nullable=False),
        sa.Column("objective", sa.String(20), nullable=False),
        sa.Column("selected_numbers", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("chosen_strategy", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_budget_plans_user_id", "budget_plans", ["user_id"])
    op.create_index("ix_budget_plans_game_id", "budget_plans", ["game_id"])


def downgrade() -> None:
    op.drop_index("ix_budget_plans_game_id", table_name="budget_plans")
    op.drop_index("ix_budget_plans_user_id", table_name="budget_plans")
    op.drop_table("budget_plans")
