"""
migrate task to deploy

Revision ID: 106230ad9e69
Revises: 16c1b29dc47c
Create Date: 2016-02-17 00:43:21.608658
"""

# revision identifiers, used by Alembic.
revision = '106230ad9e69'
down_revision = '16c1b29dc47c'

from alembic import op
import sqlalchemy as sa


MIGRATE_TASK_TO_DEPLOY = """
INSERT INTO deploy (task_id, app_id, environment, number)
SELECT id, app_id, environment, number FROM task
"""

MIGRATE_DEPLOY_TO_TASK = """
UPDATE task
SET number=deploy.number
    environment=deploy.environment
FROM deploy
WHERE task.id=deploy.task_id
"""

NEXT_VALUE_FUNCTION = """
CREATE OR REPLACE FUNCTION next_deploy_number(int, char) RETURNS int AS $$
DECLARE
  cur_app_id ALIAS FOR $1;
  cur_env ALIAS FOR $2;
  next_value int;
BEGIN
  LOOP
    UPDATE deploysequence SET value = value + 1
    WHERE app_id = cur_app_id AND environment = cur_env
    RETURNING value INTO next_value;
    IF FOUND THEN
      RETURN next_value;
    END IF;

    BEGIN
        INSERT INTO deploysequence (app_id, environment, value)
        VALUES (cur_app_id, cur_env, 1)
        RETURNING value INTO next_value;
        RETURN next_value;
    EXCEPTION WHEN unique_violation THEN
        -- do nothing
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql
"""


def upgrade():
    op.create_table(
        'deploy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(64), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['app_id'], ['app.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'app_id', 'environment', 'number', name='unq_deploy_number')
    )
    op.create_index('idx_deploy_task_id', 'deploy', ['task_id'], unique=False)
    op.create_index('idx_deploy_app_id', 'deploy', ['app_id'], unique=False)

    # Migrate the data from Task to Deploy table
    op.execute(MIGRATE_TASK_TO_DEPLOY)
    op.execute('ALTER TABLE tasksequence RENAME TO deploysequence')
    op.execute(NEXT_VALUE_FUNCTION)

    op.drop_constraint(u'unq_task_number', 'task', type_='unique')
    op.drop_column(u'task', 'environment')
    op.drop_column(u'task', 'number')

    op.execute('DROP FUNCTION IF EXISTS next_task_number(int, char)')


def downgrade():
    # Add back Task.number, as nullable
    op.add_column(u'task', sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True))

    # Migrate data from Deploy table back
    op.execute(MIGRATE_DEPLOY_TO_TASK)

    # Make column not nullable
    op.alter_column(u'task', sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_unique_constraint(u'unq_task_number', 'task', ['app_id', 'environment', 'number'])

    op.drop_index('idx_deploy_task_id', table_name='deploy')
    op.drop_index('idx_deploy_app_id', table_name='deploy')
    op.drop_table('deploy')

    op.execute('ALTER TABLE deploysequence RENAME TO tasksequence')
    op.execute("""
CREATE OR REPLACE FUNCTION next_task_number(int, char) RETURNS int AS $$
DECLARE
  cur_app_id ALIAS FOR $1;
  cur_env ALIAS FOR $2;
  next_value int;
BEGIN
  LOOP
    UPDATE tasksequence SET value = value + 1
    WHERE app_id = cur_app_id AND environment = cur_env
    RETURNING value INTO next_value;
    IF FOUND THEN
      RETURN next_value;
    END IF;

    BEGIN
        INSERT INTO tasksequence (app_id, environment, value)
        VALUES (cur_app_id, cur_env, 1)
        RETURNING value INTO next_value;
        RETURN next_value;
    EXCEPTION WHEN unique_violation THEN
        -- do nothing
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql""")
