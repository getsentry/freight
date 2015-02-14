"""
Add TaskSequence

Revision ID: 2d96d7a132ce
Revises: 4ab62120b303
Create Date: 2015-02-13 20:42:23.762204
"""

# revision identifiers, used by Alembic.
revision = '2d96d7a132ce'
down_revision = '4ab62120b303'

from alembic import op
import sqlalchemy as sa


NEXT_VALUE_FUNCTION = """
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
$$ LANGUAGE plpgsql
"""

ADD_TASK_SEQUENCES = """
INSERT INTO tasksequence (app_id, environment, value)
SELECT app_id, environment, max(id) FROM task GROUP BY app_id, environment
"""


def upgrade():
    op.create_table(
        'tasksequence',
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(64), nullable=False),
        sa.Column('value', sa.Integer(), server_default=u'0', nullable=False),
        sa.PrimaryKeyConstraint('app_id', 'environment', 'value')
    )
    op.execute(NEXT_VALUE_FUNCTION)
    op.execute(ADD_TASK_SEQUENCES)


def downgrade():
    op.execute('DROP FUNCTION IF EXISTS next_task_number(int, char)')
    op.drop_table('tasksequence')
