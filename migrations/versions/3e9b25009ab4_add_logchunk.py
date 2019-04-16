"""
Add LogChunk

Revision ID: 3e9b25009ab4
Revises: 4aea0d73027f
Create Date: 2015-02-10 19:00:30.286370
"""

# revision identifiers, used by Alembic.
revision = "3e9b25009ab4"
down_revision = "4aea0d73027f"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "logchunk",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("offset", sa.Integer(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "offset", name="unq_logchunk_source_offset"),
    )
    op.create_index("idx_logchunk_task_id", "logchunk", ["task_id"], unique=False)


def downgrade():
    op.drop_index("idx_logchunk_task_id", table_name="logchunk")
    op.drop_table("logchunk")
