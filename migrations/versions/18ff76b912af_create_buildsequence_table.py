"""
Create buildsequence table.

Revision ID: 18ff76b912af
Revises: 493c6c33fa27
Create Date: 2016-05-05 14:47:50.243970
"""

# revision identifiers, used by Alembic.
revision = '18ff76b912af'
down_revision = '493c6c33fa27'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('buildsequence',
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('app_id', 'value')
    )


def downgrade():
    op.drop_table('buildsequence')
