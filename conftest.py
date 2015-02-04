import os
import pytest
import shutil
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from alembic.config import Config
from alembic import command
from sqlalchemy import event
from sqlalchemy.orm import Session

alembic_cfg = Config(os.path.join(root, 'alembic.ini'))

from ds.config import create_app, db


@pytest.fixture(scope='session')
def session_config(request):
    db_name = 'test_ds'

    return {
        'db_name': db_name,
        'repo_root': '/tmp/ds-tests',
    }


@pytest.fixture(scope='session')
def app(request, session_config):
    app = create_app(
        _read_config=False,
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='postgresql:///' + session_config['db_name'],
        REPO_ROOT=session_config['repo_root'],
    )
    app_context = app.test_request_context()
    context = app_context.push()

    # request.addfinalizer(app_context.pop)
    return app


@pytest.fixture(scope='session', autouse=True)
def setup_db(request, app, session_config):
    db_name = session_config['db_name']
    # 9.1 does not support --if-exists
    if os.system("psql -l | grep '%s'" % db_name) == 0:
        assert not os.system('dropdb %s' % db_name)
    assert not os.system('createdb -E utf-8 %s' % db_name)

    command.upgrade(alembic_cfg, 'head')

    @event.listens_for(Session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    # TODO: find a way to kill db connections so we can dropdob
    # def teardown():
    #     os.system('dropdb %s' % db_name)

    # request.addfinalizer(teardown)


@pytest.fixture(autouse=True)
def db_session(request):
    request.addfinalizer(db.session.remove)

    db.session.begin_nested()


@pytest.fixture(autouse=True)
def clean_repo_root(request, session_config):
    repo_root = session_config['repo_root']
    shutil.rmtree(repo_root)
    os.makedirs(repo_root)
