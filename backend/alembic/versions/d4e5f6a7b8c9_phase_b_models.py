"""Phase B: prize_tiers, saved_results, user_id columns, hot_cold_summary

Revision ID: d4e5f6a7b8c9
Revises: c2d3e4f5a6b7
Create Date: 2026-03-31
"""

from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- DB-04: game_prize_tiers ---
    op.create_table(
        "game_prize_tiers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("game_definitions.id"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("match_numbers", sa.Integer(), nullable=False),
        sa.Column("match_stars", sa.Integer(), server_default="0", nullable=False),
        sa.Column("avg_prize", sa.Float(), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("game_id", "rank", name="uq_prize_tier_game_rank"),
    )
    op.create_index("ix_game_prize_tiers_game_id", "game_prize_tiers", ["game_id"])

    # --- DB-08: user_saved_results ---
    op.create_table(
        "user_saved_results",
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
            nullable=True,
        ),
        sa.Column("result_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=False),
        sa.Column("is_favorite", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_user_saved_results_user_id", "user_saved_results", ["user_id"])
    op.create_index("ix_user_saved_results_game_id", "user_saved_results", ["game_id"])
    op.create_index("ix_user_saved_results_result_type", "user_saved_results", ["result_type"])
    op.create_index("ix_user_saved_results_is_favorite", "user_saved_results", ["is_favorite"])

    # --- DB-09: user_id on scored_grids (batch mode for SQLite) ---
    with op.batch_alter_table("scored_grids") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_scored_grids_user_id", "users", ["user_id"], ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_scored_grids_user_id", ["user_id"])

    # --- DB-10: user_id on portfolios (batch mode for SQLite) ---
    with op.batch_alter_table("portfolios") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_portfolios_user_id", "users", ["user_id"], ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_portfolios_user_id", ["user_id"])

    # --- DB-11: hot_cold_summary on statistics_snapshots ---
    op.add_column("statistics_snapshots", sa.Column("hot_cold_summary", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("statistics_snapshots", "hot_cold_summary")
    with op.batch_alter_table("portfolios") as batch_op:
        batch_op.drop_index("ix_portfolios_user_id")
        batch_op.drop_constraint("fk_portfolios_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
    with op.batch_alter_table("scored_grids") as batch_op:
        batch_op.drop_index("ix_scored_grids_user_id")
        batch_op.drop_constraint("fk_scored_grids_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
    op.drop_table("user_saved_results")
    op.drop_table("game_prize_tiers")
