"""
Initial

Revision ID: 400351fa1fdf
Revises: None
Create Date: 2015-02-04 12:05:07.014006
"""

# revision identifiers, used by Alembic.
revision = '400351fa1fdf'
down_revision = None

from alembic import op
import sqlalchemy as sa
import ds


def upgrade():
    op.create_table(
        'repository',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=200), nullable=False),
        sa.Column('vcs', sa.String(length=64), nullable=False),
        sa.Column('data', ds.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'app',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=True),
        sa.Column('data', ds.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('ref', sa.String(length=128), nullable=False),
        sa.Column('sha', sa.String(length=40), nullable=False),
        sa.Column('environment', sa.String(length=64), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('data', ds.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['app_id'], ['app.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('task')
    op.drop_table('app')
    op.drop_table('user')
    op.drop_table('repository')
