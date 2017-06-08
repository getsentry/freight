"""
Create Lock table.

Revision ID: 542404c8bd48
Revises: 205fd513c96
Create Date: 2016-05-06 14:07:48.723878
"""

# revision identifiers, used by Alembic.
revision = '542404c8bd48'
down_revision = '205fd513c96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('lock',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=64), nullable=False),
        sa.Column('message', sa.String(length=140), nullable=False),
        sa.Column('date_locked', sa.DateTime(), nullable=False),
        sa.Column('date_unlocked', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['app_id'], ['app.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id',
            'app_id',
            'environment',
            'date_locked',
            name='unq_lock_number'
        )
    )
    op.create_index('idx_lock_app_id', 'lock', ['app_id'], unique=False)
    op.create_index('idx_lock_user_id', 'lock', ['user_id'], unique=False)


def downgrade():
    op.drop_index('idx_lock_user_id', table_name='lock')
    op.drop_index('idx_lock_app_id', table_name='lock')
    op.drop_table('lock')
