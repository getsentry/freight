"""
remove task.name

Revision ID: 443ea4d5c205
Revises: 4435f9f6c1da
Create Date: 2015-09-02 21:39:59.149617
"""

# revision identifiers, used by Alembic.
revision = "443ea4d5c205"
down_revision = "4435f9f6c1da"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("task", "name")


def downgrade():
    op.add_column("task", sa.Column("name", sa.String(128), nullable=False))
