"""
add task.params

Revision ID: 16c1b29dc47c
Revises: 443ea4d5c205
Create Date: 2015-09-02 21:41:59.898063
"""

# revision identifiers, used by Alembic.
revision = "16c1b29dc47c"
down_revision = "443ea4d5c205"

from alembic import op
import sqlalchemy as sa

import freight


def upgrade():
    op.add_column(
        "task",
        sa.Column("params", freight.db.types.json.JSONEncodedDict(), nullable=True),
    )


def downgrade():
    op.drop_column("task", "params")
