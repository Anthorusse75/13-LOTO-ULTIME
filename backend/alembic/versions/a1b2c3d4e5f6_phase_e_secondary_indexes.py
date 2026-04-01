"""Phase E: secondary indexes for performance (DB-16).

Revision ID: a1b2c3d4e5f6
Revises: 990d5f890631
Create Date: 2025-01-15 00:00:00.000000
"""

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "990d5f890631"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- wheeling_systems: sort by newest first
    op.create_index(
        "ix_wheeling_systems_created_at_desc",
        "wheeling_systems",
        ["created_at"],
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )

    # -- user_saved_results: quick lookup of favorites per user
    op.create_index(
        "ix_user_saved_results_user_favorite",
        "user_saved_results",
        ["user_id", "is_favorite"],
        postgresql_where="is_favorite = TRUE",
    )

    # -- user_saved_results: sort by newest first
    op.create_index(
        "ix_user_saved_results_created_at_desc",
        "user_saved_results",
        ["created_at"],
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )

    # -- user_notifications: partial index for unread notifications
    op.create_index(
        "ix_notifications_user_unread",
        "user_notifications",
        ["user_id", "is_read"],
        postgresql_where="is_read = FALSE",
    )

    # -- user_notifications: sort by newest first
    op.create_index(
        "ix_notifications_created_at_desc",
        "user_notifications",
        ["created_at"],
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )

    # -- scored_grids: partial index for played grids
    op.create_index(
        "ix_scored_grids_is_played",
        "scored_grids",
        ["is_played"],
        postgresql_where="is_played = TRUE",
    )


def downgrade() -> None:
    op.drop_index("ix_scored_grids_is_played", table_name="scored_grids")
    op.drop_index("ix_notifications_created_at_desc", table_name="user_notifications")
    op.drop_index("ix_notifications_user_unread", table_name="user_notifications")
    op.drop_index("ix_user_saved_results_created_at_desc", table_name="user_saved_results")
    op.drop_index("ix_user_saved_results_user_favorite", table_name="user_saved_results")
    op.drop_index("ix_wheeling_systems_created_at_desc", table_name="wheeling_systems")
