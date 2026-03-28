"""add is_favorite to scored_grids

Revision ID: a3b4c5d6e7f8
Revises: 6773450d8c55
Create Date: 2025-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a3b4c5d6e7f8"
down_revision = "6773450d8c55"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scored_grids",
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_scored_grids_is_favorite", "scored_grids", ["is_favorite"])


def downgrade() -> None:
    op.drop_index("ix_scored_grids_is_favorite", table_name="scored_grids")
    op.drop_column("scored_grids", "is_favorite")
