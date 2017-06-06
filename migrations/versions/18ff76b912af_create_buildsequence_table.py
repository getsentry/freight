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

NEXT_VALUE_FUNCTION = """
CREATE OR REPLACE FUNCTION next_build_number(int) RETURNS int AS $$
DECLARE
  cur_app_id ALIAS FOR $1;
  next_value int;
BEGIN
  LOOP
    UPDATE buildsequence SET value = value + 1
    WHERE app_id = cur_app_id
    RETURNING value INTO next_value;
    IF FOUND THEN
      RETURN next_value;
    END IF;

    BEGIN
        INSERT INTO buildsequence (app_id, value)
        VALUES (cur_app_id, 1)
        RETURNING value INTO next_value;
        RETURN next_value;
    EXCEPTION WHEN unique_violation THEN
        -- do nothing
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql
"""

ADD_BUILD_SEQUENCES = """
INSERT INTO buildsequence (app_id, value)
SELECT app_id, max(id) FROM build GROUP BY app_id
"""


def upgrade():
    op.create_table('buildsequence',
        sa.Column('app_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('app_id', 'value')
    )
    op.execute(NEXT_VALUE_FUNCTION)
    op.execute(ADD_BUILD_SEQUENCES)


def downgrade():
    op.execute('DROP FUNCTION IF EXISTS next_build_number(int)')
    op.drop_table('buildsequence')
