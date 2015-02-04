from __future__ import absolute_import

import os

from subprocess import PIPE, Popen

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path):
        self.path = path

    def run(self, *args, **kwargs):
        kwargs.setdefault('cwd', self.path)

        env = os.environ.copy()
        for key, value in kwargs.pop('env', {}):
            env[key] = value

        kwargs['env'] = env
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE

        proc = Popen(*args, **kwargs)
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            raise CommandError(args[0], proc.returncode, stdout, stderr)
        return stdout
