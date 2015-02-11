from __future__ import absolute_import

import os
import traceback

from subprocess import Popen, PIPE

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path, logbuffer=PIPE):
        self.path = path
        self.logbuffer = logbuffer

    def run(self, command, *args, **kwargs):
        kwargs.setdefault('cwd', self.path)

        env = os.environ.copy()
        for key, value in kwargs.pop('env', {}).iteritems():
            env[key] = value

        kwargs['env'] = env

        kwargs['stdout'] = self.logbuffer
        kwargs['stderr'] = self.logbuffer

        self.logbuffer.write('>> Running {}\n'.format(command))
        try:
            proc = Popen(command, *args, **kwargs)
        except OSError:
            self.logbuffer.write(traceback.format_exc())
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            raise CommandError(command, proc.returncode, stdout, stderr)
        return stdout
