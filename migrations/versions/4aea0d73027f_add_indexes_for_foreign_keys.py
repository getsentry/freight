"""
Add indexes for foreign keys

Revision ID: 4aea0d73027f
Revises: 2dfcb1aa3324
Create Date: 2015-02-10 18:37:23.963251
"""

# revision identifiers, used by Alembic.
revision = '4aea0d73027f'
down_revision = '2dfcb1aa3324'

from alembic import op


def upgrade():
    op.create_index('idx_app_repository_id', 'app', ['repository_id'], unique=False)
    op.create_index('idx_task_app_id', 'task', ['app_id'], unique=False)
    op.create_index('idx_task_user_id', 'task', ['user_id'], unique=False)


def downgrade():
    op.drop_index('idx_task_user_id', table_name='task')
    op.drop_index('idx_task_app_id', table_name='task')
    op.drop_index('idx_app_repository_id', table_name='app')
