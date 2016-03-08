"""
Added TaskConfig

Revision ID: 205fd513c96
Revises: 106230ad9e69
Create Date: 2016-03-07 13:27:04.392376
"""

# revision identifiers, used by Alembic.
revision = '205fd513c96'
down_revision = '106230ad9e69'

from alembic import op
from sqlalchemy.sql import table
import sqlalchemy as sa
import freight


def upgrade():
    taskconfig_table = op.create_table(
        'taskconfig',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('type', sa.Integer(), nullable=True),
        sa.Column('data', freight.db.types.json.JSONEncodedDict(), nullable=True),
        sa.ForeignKeyConstraint(['app_id'], ['app.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('app_id', 'type', name='unq_app_id_type')
    )
    op.create_index('idx_taskconfig_app_id', 'taskconfig', ['app_id'], unique=False)
    op.create_index('idx_taskconfig_type', 'taskconfig', ['type'], unique=False)

    connection = op.get_bind()

    app_table = table(
        'app',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=54), nullable=False),
        sa.Column('data', freight.db.types.json.JSONEncodedDict(), nullable=True)
    )

    # Copy over the existing configs out of the App table and into TaskConfigs
    for app in connection.execute(app_table.select()):
        print("Migrating App id=%s" % app.id)

        op.bulk_insert(
            taskconfig_table,
            [
                {'app_id': app.id, 'type': 0, 'provider': app.provider, 'data': app.data},
            ],
        )


def downgrade():
    op.drop_index('idx_taskconfig_type', table_name='taskconfig')
    op.drop_index('idx_taskconfig_app_id', table_name='taskconfig')
    op.drop_table('taskconfig')
