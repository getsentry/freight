from __future__ import absolute_import

import os
import shlex
import traceback

from subprocess import Popen

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path, stdout=None, stderr=None):
        self.path = path
        self.stdout = stdout
        self.stderr = stderr

    def whereis(self, program, env):
        for path in env.get('PATH', '').split(':'):
            if os.path.exists(os.path.join(path, program)) and \
               not os.path.isdir(os.path.join(path, program)):
                return os.path.join(path, program)
        return None

    def run(self, command, *args, **kwargs):
        kwargs.setdefault('cwd', self.path)

        if isinstance(command, basestring):
            command = shlex.split(command)

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
            if not self.whereis(env, command[0]):
                if self.stderr:
                    self.stderr.write('Command not found: {}'.format(command[0]))
            else:
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
