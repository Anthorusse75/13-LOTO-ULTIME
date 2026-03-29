"""add is_played and played_at to scored_grids

Revision ID: b1c2d3e4f5a6
Revises: a3b4c5d6e7f8
Create Date: 2026-03-29 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5a6"
down_revision = "a3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scored_grids",
        sa.Column("is_played", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column(
        "scored_grids",
        sa.Column("played_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_scored_grids_is_played", "scored_grids", ["is_played"])


def downgrade() -> None:
    op.drop_index("ix_scored_grids_is_played", table_name="scored_grids")
    op.drop_column("scored_grids", "played_at")
    op.drop_column("scored_grids", "is_played")
