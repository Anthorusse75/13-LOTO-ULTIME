"""make all datetime columns timezone-aware

Revision ID: 78d468fdbb48
Revises: b1c2d3e4f5a6
Create Date: 2026-03-31 10:46:14.927075
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78d468fdbb48'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All DateTime columns that need TIMESTAMP WITH TIME ZONE
_COLUMNS = [
    ("users", "last_login", True),
    ("users", "created_at", False),
    ("users", "updated_at", True),
    ("draws", "created_at", False),
    ("draws", "updated_at", True),
    ("game_definitions", "created_at", False),
    ("game_definitions", "updated_at", True),
    ("job_executions", "started_at", False),
    ("job_executions", "finished_at", True),
    ("scored_grids", "computed_at", False),
    ("scored_grids", "played_at", True),
    ("statistics_snapshots", "computed_at", False),
    ("portfolios", "computed_at", False),
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table, column, nullable in _COLUMNS:
            op.alter_column(
                table,
                column,
                type_=sa.DateTime(timezone=True),
                existing_type=sa.DateTime(),
                existing_nullable=nullable,
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table, column, nullable in _COLUMNS:
            op.alter_column(
                table,
                column,
                type_=sa.DateTime(),
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=nullable,
            )
