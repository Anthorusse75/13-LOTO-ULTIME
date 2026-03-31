"""add grid_draw_results and user_notifications tables

Revision ID: 990d5f890631
Revises: f1a2b3c4d5e6
Create Date: 2026-03-31 22:50:12.135839
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '990d5f890631'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('message', sa.String(length=1000), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_read', 'user_notifications', ['user_id', 'is_read'], unique=False)
    op.create_index(op.f('ix_user_notifications_user_id'), 'user_notifications', ['user_id'], unique=False)
    op.create_table('grid_draw_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scored_grid_id', sa.Integer(), nullable=False),
    sa.Column('draw_id', sa.Integer(), nullable=False),
    sa.Column('matched_numbers', sa.JSON(), nullable=False),
    sa.Column('matched_stars', sa.JSON(), nullable=True),
    sa.Column('match_count', sa.Integer(), nullable=False),
    sa.Column('star_match_count', sa.Integer(), nullable=False),
    sa.Column('prize_rank', sa.Integer(), nullable=True),
    sa.Column('estimated_prize', sa.Float(), nullable=False),
    sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['draw_id'], ['draws.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['scored_grid_id'], ['scored_grids.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_grid_draw_results_draw', 'grid_draw_results', ['draw_id'], unique=False)
    op.create_index('ix_grid_draw_results_grid', 'grid_draw_results', ['scored_grid_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_grid_draw_results_grid', table_name='grid_draw_results')
    op.drop_index('ix_grid_draw_results_draw', table_name='grid_draw_results')
    op.drop_table('grid_draw_results')
    op.drop_index(op.f('ix_user_notifications_user_id'), table_name='user_notifications')
    op.drop_index('ix_notifications_user_read', table_name='user_notifications')
    op.drop_table('user_notifications')
