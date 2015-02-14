"""
Add Task.number

Revision ID: 583090bcc922
Revises: 2d96d7a132ce
Create Date: 2015-02-13 20:48:50.820276
"""

# revision identifiers, used by Alembic.
revision = '583090bcc922'
down_revision = '2d96d7a132ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('task', sa.Column('number', sa.Integer(), nullable=False))
    op.create_unique_constraint(u'unq_task_number', 'task', ['app_id', 'environment', 'number'])


def downgrade():
    op.drop_constraint(u'unq_task_number', 'task', type_='unique')
    op.drop_column('task', 'number')
