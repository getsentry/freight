from __future__ import absolute_import

import os
import traceback

from subprocess import Popen

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path, stdout=None, stderr=None):
        self.path = path
        self.stdout = stdout
        self.stderr = stderr

    def run(self, command, *args, **kwargs):
        kwargs.setdefault('cwd', self.path)

        env = os.environ.copy()
        for key, value in kwargs.pop('env', {}).iteritems():
            env[key] = value

        kwargs['env'] = env

        kwargs['stdout'] = self.stdout
        kwargs['stderr'] = self.stderr

        self.stdout.write('>> Running {}\n'.format(command))
        try:
            proc = Popen(command, *args, **kwargs)
        except OSError:
            if self.stderr:
                self.stderr.write(traceback.format_exc())
            raise

        if kwargs.get('capture'):
            (stdout, stderr) = proc.communicate()
        else:
            stdout, stderr = None, None
            proc.wait()

        if proc.returncode != 0:
            raise CommandError(command, proc.returncode, stdout, stderr)
        return stdout
