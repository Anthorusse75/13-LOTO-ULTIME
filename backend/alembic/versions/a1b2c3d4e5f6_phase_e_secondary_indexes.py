"""Phase E: secondary indexes for performance (DB-16).

Revision ID: a1b2c3d4e5f6
Revises: 990d5f890631
Create Date: 2025-01-15 00:00:00.000000
"""

from alembic import op
from sqlalchemy import text

revision = "a1b2c3d4e5f6"
down_revision = "990d5f890631"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # -- wheeling_systems: sort by newest first
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_wheeling_systems_created_at_desc "
        "ON wheeling_systems USING btree (created_at DESC)"
    ))

    # -- user_saved_results: quick lookup of favorites per user (partial)
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_user_saved_results_user_favorite "
        "ON user_saved_results (user_id, is_favorite) WHERE is_favorite = TRUE"
    ))

    # -- user_saved_results: sort by newest first
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_user_saved_results_created_at_desc "
        "ON user_saved_results USING btree (created_at DESC)"
    ))

    # -- user_notifications: partial index for unread notifications
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_unread "
        "ON user_notifications (user_id, is_read) WHERE is_read = FALSE"
    ))

    # -- user_notifications: sort by newest first
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_notifications_created_at_desc "
        "ON user_notifications USING btree (created_at DESC)"
    ))

    # -- scored_grids: replace the plain index with a partial index for played grids
    # Drop the auto-generated non-partial index first (from model index=True)
    conn.execute(text(
        "DROP INDEX IF EXISTS ix_scored_grids_is_played"
    ))
    conn.execute(text(
        "CREATE INDEX ix_scored_grids_played_partial "
        "ON scored_grids (is_played) WHERE is_played = TRUE"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DROP INDEX IF EXISTS ix_scored_grids_played_partial"))
    # Restore the original non-partial index
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_scored_grids_is_played "
        "ON scored_grids (is_played)"
    ))
    conn.execute(text("DROP INDEX IF EXISTS ix_notifications_created_at_desc"))
    conn.execute(text("DROP INDEX IF EXISTS ix_notifications_user_unread"))
    conn.execute(text("DROP INDEX IF EXISTS ix_user_saved_results_created_at_desc"))
    conn.execute(text("DROP INDEX IF EXISTS ix_user_saved_results_user_favorite"))
    conn.execute(text("DROP INDEX IF EXISTS ix_wheeling_systems_created_at_desc"))
