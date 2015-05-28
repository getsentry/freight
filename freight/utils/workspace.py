from __future__ import absolute_import

import logging
import os
import shlex
import shutil
import sys
import traceback

from flask import current_app
from subprocess import PIPE, Popen, STDOUT
from uuid import uuid1

from freight.exceptions import CommandError


class Workspace(object):
    log = logging.getLogger('workspace')

    def __init__(self, path, log=None):
        self.path = path
        if log is not None:
            self.log = log

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
        command = map(str, command)

        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        if kwargs.get('env'):
            for key, value in kwargs['env'].iteritems():
                env[key] = value

        kwargs['env'] = env
        kwargs['bufsize'] = 0

        self.log.info('Running {}'.format(command))
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

    def remove(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)


class TemporaryWorkspace(Workspace):
    def __init__(self, *args, **kwargs):
        path = os.path.join(
            current_app.config['WORKSPACE_ROOT'],
            'freight-workspace-{}'.format(uuid1().hex),
        )
        super(TemporaryWorkspace, self).__init__(path, *args, **kwargs)
