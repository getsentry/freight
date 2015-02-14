from __future__ import absolute_import, unicode_literals

__all__ = ['Provider']

from flask import current_app
from tempfile import NamedTemporaryFile


class Provider(object):
    name = None

    def get_default_options(self):
        return {
            'timeout': {},
        }

    def get_options(self):
        return {}

    def execute(self, workspace, task):
        raise NotImplementedError

    def get_ssh_key(self):
        if not current_app.config['SSH_PRIVATE_KEY']:
            return

        f = NamedTemporaryFile()
        f.write(current_app.config['SSH_PRIVATE_KEY'])
        f.flush()
        f.seek(0)

        return f
