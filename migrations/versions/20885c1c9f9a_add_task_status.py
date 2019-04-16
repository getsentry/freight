"""
Add Task.status

Revision ID: 20885c1c9f9a
Revises: 400351fa1fdf
Create Date: 2015-02-04 14:00:55.505019
"""

# revision identifiers, used by Alembic.
revision = "20885c1c9f9a"
down_revision = "400351fa1fdf"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("task", sa.Column("status", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("task", "status")
