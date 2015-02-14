"""
Allow Task.sha null

Revision ID: 4ab62120b303
Revises: 3e9b25009ab4
Create Date: 2015-02-13 19:30:32.963750
"""

# revision identifiers, used by Alembic.
revision = '4ab62120b303'
down_revision = '3e9b25009ab4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('task', 'sha',
               existing_type=sa.VARCHAR(length=40),
               nullable=True)


def downgrade():
    op.alter_column('task', 'sha',
               existing_type=sa.VARCHAR(length=40),
               nullable=False)
