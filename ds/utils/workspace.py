from __future__ import absolute_import, unicode_literals

import logging
import os
import shlex
import sys
import traceback

from subprocess import PIPE, Popen, STDOUT

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path):
        self.path = path
        self.log = logging.getLogger('workspace')

    def whereis(self, program, env):
        for path in env.get('PATH', '').split(':'):
            if os.path.exists(os.path.join(path, program)) and \
               not os.path.isdir(os.path.join(path, program)):
                return os.path.join(path, program)
        return None

    def _get_writer(self, pipe):
        if not isinstance(pipe, int):
            pipe = pipe.fileno()
        return os.fdopen(pipe, 'w')

    def _run_process(self, command, *args, **kwargs):
        stdout = kwargs.get('stdout', sys.stdout)
        stderr = kwargs.get('stderr', sys.stderr)

        kwargs.setdefault('cwd', self.path)

        if isinstance(command, basestring):
            command = shlex.split(command)

        env = os.environ.copy()
        for key, value in kwargs.pop('env', {}).iteritems():
            env[key] = value

        kwargs['env'] = env

        self.log.info('>> Running {}'.format(command))
        try:
            proc = Popen(command, *args, **kwargs)
        except OSError as exc:
            if not self.whereis(command[0], env):
                msg = 'ERROR: Command not found: {}'.format(command[0])
            else:
                msg = traceback.format_exc()
            raise CommandError(command, 1, stdout=None, stderr=msg)

        return proc

    def capture(self, command, *args, **kwargs):
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = STDOUT
        proc = self._run_process(command, *args, **kwargs)
        (stdout, stderr) = proc.communicate()

        if proc.returncode != 0:
            raise CommandError(command, proc.returncode, stdout, stderr)

        return stdout

    def run(self, command, *args, **kwargs):
        proc = self._run_process(command, *args, **kwargs)
        proc.wait()

        if proc.returncode != 0:
            raise CommandError(command, proc.returncode)
