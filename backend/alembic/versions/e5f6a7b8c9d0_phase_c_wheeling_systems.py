"""Phase C: wheeling_systems table

Revision ID: e5f6a7b8c9d0
Revises: 7bcd4a4c4933
Create Date: 2026-03-31
"""

from alembic import op
import sqlalchemy as sa

revision = "e5f6a7b8c9d0"
down_revision = "7bcd4a4c4933"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wheeling_systems",
        sa.Column("id", sa.Integer(), primary_key=True),
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
        sa.Column("selected_numbers", sa.JSON(), nullable=False),
        sa.Column("selected_stars", sa.JSON(), nullable=True),
        sa.Column("guarantee_level", sa.Integer(), nullable=False),
        sa.Column("grids", sa.JSON(), nullable=False),
        sa.Column("grid_count", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Float(), nullable=False),
        sa.Column("coverage_rate", sa.Float(), nullable=False),
        sa.Column("reduction_rate", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wheeling_systems_user_id", "wheeling_systems", ["user_id"])
    op.create_index("ix_wheeling_systems_game_id", "wheeling_systems", ["game_id"])


def downgrade() -> None:
    op.drop_index("ix_wheeling_systems_game_id", "wheeling_systems")
    op.drop_index("ix_wheeling_systems_user_id", "wheeling_systems")
    op.drop_table("wheeling_systems")
