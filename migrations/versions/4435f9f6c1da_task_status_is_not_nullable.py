"""
Task.status is not nullable

Revision ID: 4435f9f6c1da
Revises: 583090bcc922
Create Date: 2015-02-19 18:54:57.678036
"""

# revision identifiers, used by Alembic.
revision = '4435f9f6c1da'
down_revision = '583090bcc922'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('task', 'status', existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    op.alter_column('task', 'status', existing_type=sa.INTEGER(), nullable=True)
