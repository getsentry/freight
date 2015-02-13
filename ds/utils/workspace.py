from __future__ import absolute_import

import os
import shlex
import traceback

from subprocess import PIPE, Popen, STDOUT
from time import sleep

from ds.exceptions import CommandError


class Workspace(object):
    def __init__(self, path, on_log_chunk=None, chunk_size=4096):
        self.path = path
        self.on_log_chunk = on_log_chunk
        self.chunk_size = chunk_size

    def _flush_output(self, proc):
        chunk_size = self.chunk_size
        on_log_chunk = self.on_log_chunk
        result = ''
        while True:
            is_running = proc.poll() is None
            chunk = proc.stdout.read()
            if not (is_running or chunk):
                break

            while chunk:
                result += chunk
                while len(result) >= chunk_size:
                    newline_pos = result.rfind('\n', 0, chunk_size)
                    if newline_pos == -1:
                        newline_pos = chunk_size
                    else:
                        newline_pos += 1
                    on_log_chunk(result[:newline_pos])
                    result = result[newline_pos:]
                chunk = proc.stdout.read()
            sleep(0.1)

        if result:
            on_log_chunk(result)

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

        if self.on_log_chunk:
            kwargs['stderr'] = STDOUT
            kwargs['stdout'] = PIPE

        msg = '>> Running {}\n'.format(command)
        if self.on_log_chunk:
            self.on_log_chunk(msg)

        try:
            proc = Popen(command, *args, **kwargs)
        except OSError:
            if not self.whereis(env, command[0]):
                error = 'Command not found: {}'.format(command[0])
            else:
                error = traceback.format_exc()
            if self.on_log_chunk:
                self.on_log_chunk(error)
            raise

        if self.on_log_chunk:
            proc.stdout.flush()
            self._flush_output(proc)
        proc.wait()

        if proc.returncode != 0:
            raise CommandError(command, proc.returncode)
