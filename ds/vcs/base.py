from __future__ import absolute_import, unicode_literals

import os
import os.path

from ds.constants import PROJECT_ROOT
from ds.exceptions import CommandError


class UnknownRevision(CommandError):
    pass


class Vcs(object):
    ssh_connect_path = os.path.join(PROJECT_ROOT, 'bin', 'ssh-connect')

    def __init__(self, workspace, url, username=None):
        self.url = url
        self.username = username
        self.workspace = workspace

        self._path_exists = None

    @property
    def path(self):
        return self.workspace.path

    def get_default_env(self):
        return {}

    def run(self, command, capture=False, *args, **kwargs):
        if not self.exists():
            kwargs.setdefault('cwd', None)

        env = kwargs.pop('env', {})
        for key, value in self.get_default_env().iteritems():
            env.setdefault(key, value)
        env.setdefault('DS_SSH_REPO', self.url)
        kwargs['env'] = env

        if capture:
            handler = self.workspace.capture
        else:
            handler = self.workspace.run

        rv = handler(command, *args, **kwargs)
        if isinstance(rv, basestring):
            return rv.strip()
        return rv

    def exists(self):
        return os.path.exists(self.workspace.path)

    def clone(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def checkout(self, ref):
        raise NotImplementedError

    def describe(self, ref):
        """
        Given a `ref` return the fully qualified version.
        """
        raise NotImplementedError

    def get_default_revision(self):
        raise NotImplementedError
