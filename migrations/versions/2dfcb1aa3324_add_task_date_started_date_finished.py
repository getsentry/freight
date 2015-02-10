"""
Add Task.{date_started,date_finished}

Revision ID: 2dfcb1aa3324
Revises: 20885c1c9f9a
Create Date: 2015-02-09 21:21:52.928819
"""

# revision identifiers, used by Alembic.
revision = '2dfcb1aa3324'
down_revision = '20885c1c9f9a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('task', sa.Column('date_finished', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('date_started', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('task', 'date_started')
    op.drop_column('task', 'date_finished')
