import os
import pytest
import shutil
import subprocess

from alembic import command
from alembic.config import Config

from sqlalchemy.orm import session
from freight.config import create_app, db
from freight.constants import PROJECT_ROOT

ALEMBIC_CONFIG = Config(os.path.join(PROJECT_ROOT, "alembic.ini"))

os.environ["FREIGHT_CONF"] = os.path.join(PROJECT_ROOT, "tests", "config.py")


@pytest.fixture(autouse=True, scope="session")
def app(request):
    app = create_app(REDIS_URL="redis://localhost/9")
    app_context = app.test_request_context()
    app_context.push()
    return app


def pytest_runtest_teardown(item):
    from redis import StrictRedis

    client = StrictRedis(db=9)
    client.flushdb()


@pytest.fixture(autouse=True)
def clean_workspace_root(request, app):
    path = app.config["WORKSPACE_ROOT"]
    if os.path.exists(path):
        print(f"Cleaning up workspace root: {path}")
        shutil.rmtree(path)
    os.makedirs(path)


@pytest.fixture(scope="session", autouse=True)
def reset_database(request, app):
    _reset_database(request, app)
    return lambda: _reset_database(request, app)


def _reset_database(request, app):
    db_name = "test_freight"

    session.close_all_sessions()

    # 9.1 does not support --if-exists
    if subprocess.call(f"psql -l | grep '{db_name}'", shell=True) == 0:
        engine = db.engine
        engine.connect().close()
        engine.dispose()
        subprocess.check_call(f"dropdb {db_name}", shell=True)

    subprocess.check_call(f"createdb -E utf-8 {db_name}", shell=True)

    command.upgrade(ALEMBIC_CONFIG, "head")
    return lambda: reset_database(request, app)
