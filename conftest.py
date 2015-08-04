import os
import pytest
import shutil
import subprocess

from alembic import command
from alembic.config import Config

from freight.config import create_app, db
from freight.constants import PROJECT_ROOT

ALEMBIC_CONFIG = Config(os.path.join(PROJECT_ROOT, 'alembic.ini'))

os.environ['FREIGHT_CONF'] = os.path.join(PROJECT_ROOT, 'tests', 'config.py')


@pytest.fixture(autouse=True, scope='session')
def app(request):
    app = create_app(REDIS_URL='redis://localhost/9')
    app_context = app.test_request_context()
    app_context.push()
    return app


def pytest_runtest_teardown(item):
    from redis import StrictRedis
    client = StrictRedis(db=9)
    client.flushdb()


@pytest.fixture(autouse=True)
def clean_workspace_root(request, app):
    path = app.config['WORKSPACE_ROOT']
    if os.path.exists(path):
        print('Cleaning up workspace root: {}'.format(path))
        shutil.rmtree(path)
    os.makedirs(path)


@pytest.fixture(scope='session', autouse=True)
def reset_database(request, app):
    db_name = 'test_freight'

    db.session.close_all()

    # 9.1 does not support --if-exists
    if subprocess.call("psql -l | grep '%s'" % db_name, shell=True) == 0:
        engine = db.engine
        engine.connect().close()
        engine.dispose()
        subprocess.check_call('dropdb %s' % db_name, shell=True)

    subprocess.check_call('createdb -E utf-8 %s' % db_name, shell=True)

    command.upgrade(ALEMBIC_CONFIG, 'head')
    return lambda: reset_database(request, app)
