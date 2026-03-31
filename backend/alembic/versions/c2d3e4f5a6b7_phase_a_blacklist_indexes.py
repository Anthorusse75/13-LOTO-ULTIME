"""Phase A: token_blacklist table + composite indexes

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-05 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # DB-01: token_blacklist table
    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jti", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.Float(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_token_blacklist_jti", "token_blacklist", ["jti"], unique=True)

    # DB-02: composite index on scored_grids(game_id, total_score)
    op.create_index(
        "ix_scored_grids_game_score",
        "scored_grids",
        ["game_id", "total_score"],
    )

    # DB-03: composite index on draws(game_id, draw_date)
    op.create_index(
        "ix_draws_game_date_desc",
        "draws",
        ["game_id", "draw_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_draws_game_date_desc", table_name="draws")
    op.drop_index("ix_scored_grids_game_score", table_name="scored_grids")
    op.drop_index("ix_token_blacklist_jti", table_name="token_blacklist")
    op.drop_table("token_blacklist")
