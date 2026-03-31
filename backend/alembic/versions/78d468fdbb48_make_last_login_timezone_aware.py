"""make last_login timezone-aware

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


def upgrade() -> None:
    # Convert last_login from TIMESTAMP to TIMESTAMP WITH TIME ZONE
    # PostgreSQL: ALTER COLUMN TYPE does the conversion automatically
    # SQLite: no-op (no distinction between tz-aware and tz-naive)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "users",
            "last_login",
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(),
            existing_nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "users",
            "last_login",
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )
