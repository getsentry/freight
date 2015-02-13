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
        'workspace_root': '/tmp/ds-tests',
    }


@pytest.fixture(scope='session')
def app(request, session_config):
    app = create_app(
        _read_config=False,
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='postgresql:///' + session_config['db_name'],
        WORKSPACE_ROOT=session_config['workspace_root'],
        SSH_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEArvyc+vZVxUjC5ZcFg1VN3jQOCOjO94gwQKFxlz0zOCrCz+Sq\nnWk28YdUpOU016Zinlh4ZZk2136nCKKTMnNMjd6cTTCn5fWomjR+F2CSdaYYpYfO\nNtVnq0SIDUgGmjyPncOGrxVT6EzjjSvgE8W8YIc5rVJqNMAH5OywUH0nqISYN2yP\nwbUPVf8zqu3kpnTt7YcWZ+Ye4b3jX6Fo2Xw5P1TTwQ92K9JdVAltBRpwSLtBQUYC\nMkwtNf6QIbRYKoVZuEhi/8XCxT0zG78Lsqpbld8IEnLWUGifCtx9mKqVi8Y3QTsT\nknMWFaf+Su8htgw/W7tufmrtTKNJYDtPTGiBeQIDAQABAoIBABYsC/gAnn2Q6qEM\nsbYiaOtuzRhz50WWDAckbbAsIQFM6cJNxxCK9FtGOoNqR3fLrVNDAn5dG4XSlneR\nofUShvCy9DsTnzKUHfjsDc4IfoZJtXXD720jPS+GT3bfWXbRlaD31Wj52tfkZjDN\nDmdy9puEhtpfRvXIHzfyhaStNwkzDh0jp8e8yok1mLA+3FPqkJPF6ptxPs6HEQS8\npY75jxvypbux2+W9249J/HqMmd5/+r7tt62vciqnXb2LG2AmUxLhTAQU9mGM2OSL\nrh2j+7/2apEQLdJ0DbS19IkQZRpO/DLPyhg6C29ZuNQffQWoLiZlfgIEaBT939aM\nkFdzy8ECgYEA4BdisLRCyCdm2M7fMDsV7j71z48Q1Kdl5A6/ngiK1dCwnjRMvkLx\nKOHtmvpJxHTH+JAewrrGUg0GF1YpM3gi0FQ7f9qTlAeFIrU3udV8F/m6+rIOpx92\nB2FSrYTaonLX8g4OzXKNtQcwzx91mFWTIEmfQl9let0WMrCRzReXp0sCgYEAx+dC\ncbERCVcJvs9+SUwVXXOreCF4PedLrg7bjkfYSpmAJk9c36EOi1jIGO5rat5/k7Nb\n0plWghADjtcb4r8oO6pzhMR81cESgFOk1UasP4rPYX4mEYPBwVGgN7ECUXj9XFPZ\n/tk7lgneBc1/6eV978MTprXiHU5Rv7yZBMuf68sCgYAd6YE27Rjs9rV3w0VvfrOS\ntbzCE+q/OAkVxBI32hQOLmkk9P45d14RgvbgdQBbxOrcdwBkJeJLGYnym4GsaSDc\nhiHbEyYX4FkZJO9nUuPZn3Ah/pqOHFj46zjKCK3WeVXx7YZ0ThI0U91kCGL+Do4x\nBSLJDUrSd6h6467SnY+UuQKBgGV0/AYT5h+lay7KxL+Su+04Pbi01AAnGgP3SnuF\n/0KtcZsAAJUHewhCQRxWNXKCBqICEAJtDLjqQ8QFbQPCHTtbIVIrH2ilmyxCR5Bv\nVBDT9Lj4e328L2Rcd0KMti5/h6eKb0OnIVTfIS40xE0Dys0bZyfffCl/jIIRyF/k\nsP/NAoGBAIfxtr881cDFrxahrTJ3AtGXxjJjMUW/S6+gKd7Lj9i+Uadb9vjD8Wt8\ngWrUDwXVAhD5Sxv+OCBizPF1CxXTgC3+/ophkUcy5VTcBchgQI7JrItujxUc0EvR\nCwA7/JPyO8DaUtvpodUKO27vr11G/NmXYrOohCP6VxH/Y6p5L9o4\n-----END RSA PRIVATE KEY-----"
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
def clean_workspace_root(request, session_config):
    path = session_config['workspace_root']
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
