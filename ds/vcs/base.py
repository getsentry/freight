from __future__ import absolute_import

import os
import os.path

from subprocess import Popen, PIPE

from ds.constants import PROJECT_ROOT
from ds.exceptions import CommandError


class UnknownRevision(CommandError):
    pass


class BufferParser(object):
    def __init__(self, fp, delim):
        self.fp = fp
        self.delim = delim

    def __iter__(self):
        chunk_buffer = []
        for chunk in self.fp:
            while chunk.find(self.delim) != -1:
                d_pos = chunk.find(self.delim)

                chunk_buffer.append(chunk[:d_pos])

                yield ''.join(chunk_buffer)
                chunk_buffer = []

                chunk = chunk[d_pos + 1:]

            if chunk:
                chunk_buffer.append(chunk)

        if chunk_buffer:
            yield ''.join(chunk_buffer)


class Vcs(object):
    ssh_connect_path = os.path.join(PROJECT_ROOT, 'bin', 'ssh-connect')

    def __init__(self, path, url, username=None):
        self.path = path
        self.url = url
        self.username = username

        self._path_exists = None

    def get_default_env(self):
        return {}

    def run(self, *args, **kwargs):
        if self.exists():
            kwargs.setdefault('cwd', self.path)

        env = os.environ.copy()

        for key, value in self.get_default_env().iteritems():
            env.setdefault(key, value)

        env.setdefault('DS_SSH_REPO', self.url)

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

    def exists(self):
        return os.path.exists(self.path)

    def clone(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def checkout(self, ref):
        raise NotImplementedError

    def log(self, parent=None, offset=0, limit=100):
        """
        Gets the commit log for the repository.

        :param parent: Parent at which revision search begins.
        :param offset: An offset into the results at which to begin.
        :param limit: The maximum number of results to return.
        :return: A list of <RevisionResult> matching the given criteria.
        """
        raise NotImplementedError

    def get_default_revision(self):
        raise NotImplementedError


class RevisionResult(object):
    def __init__(self, id, message, author, author_date, committer=None,
                 committer_date=None):
        self.id = id
        self.message = message
        self.author = author
        self.author_date = author_date
        self.committer = committer or author
        self.committer_date = committer_date or author_date

    def __repr__(self):
        return '<%s: id=%r author=%r subject=%r>' % (
            type(self).__name__, self.id, self.author, self.subject)

    @property
    def subject(self):
        return self.message.splitlines()[0]
