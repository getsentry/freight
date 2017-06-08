"""
Create build table.

Revision ID: 493c6c33fa27
Revises: 205fd513c96
Create Date: 2016-05-05 14:31:38.491777
"""

# revision identifiers, used by Alembic.
revision = '493c6c33fa27'
down_revision = '205fd513c96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('build',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['app_id'], ['app.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'app_id', 'number', name='unq_build_number')
    )
    op.create_index('idx_build_app_id', 'build', ['app_id'], unique=False)
    op.create_index('idx_build_task_id', 'build', ['task_id'], unique=False)


def downgrade():
    op.drop_index('idx_build_task_id', table_name='build')
    op.drop_index('idx_build_app_id', table_name='build')
    op.drop_table('build')
