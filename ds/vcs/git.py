from __future__ import absolute_import

__all__ = ['GitVcs']

from datetime import datetime
from urlparse import urlparse

from .base import (
    Vcs, RevisionResult, BufferParser, CommandError, UnknownRevision
)


LOG_FORMAT = '%H\x01%an <%ae>\x01%at\x01%cn <%ce>\x01%ct\x01%P\x01%B\x02'


class GitVcs(Vcs):
    binary_path = 'git'

    def get_default_env(self):
        return {
            'GIT_SSH': self.ssh_connect_path,
        }

    def get_default_revision(self):
        return 'master'

    @property
    def remote_url(self):
        if self.url.startswith(('ssh:', 'http:', 'https:')):
            parsed = urlparse(self.url)
            port = (':%s' % (parsed.port,) if parsed.port else '')
            url = '%s://%s@%s/%s' % (
                parsed.scheme,
                parsed.username or self.username or 'git',
                parsed.hostname + port,
                parsed.path.lstrip('/'),
            )
        else:
            url = self.url
        return url

    def run(self, cmd, **kwargs):
        cmd = [self.binary_path] + cmd
        try:
            return super(GitVcs, self).run(cmd, **kwargs)
        except CommandError as e:
            if 'unknown revision or path' in e.stderr:
                raise UnknownRevision(
                    cmd=e.cmd,
                    retcode=e.retcode,
                    stdout=e.stdout,
                    stderr=e.stderr,
                )
            raise

    def clone(self):
        self.run(['clone', self.remote_url, self.path])

    def update(self):
        self.run(['fetch', '--all', '-p'])

    def checkout(self, ref):
        self.run(['reset' '--hard', ref])

    def log(self, parent=None, offset=0, limit=100):
        cmd = ['log', '--date-order', '--pretty=format:%s' % (LOG_FORMAT,)]

        if offset:
            cmd.append('--skip=%d' % (offset,))
        if limit:
            cmd.append('--max-count=%d' % (limit,))

        if not parent:
            cmd.append('--all')
        else:
            cmd.append(parent)

        result = self.run(cmd)
        for chunk in BufferParser(result, '\x02'):
            (sha, author, author_date, committer, committer_date,
             parents, message) = chunk.split('\x01')

            # sha may have a trailing newline due to git log adding it
            sha = sha.lstrip('\n')

            author_date = datetime.utcfromtimestamp(float(author_date))
            committer_date = datetime.utcfromtimestamp(float(committer_date))

            yield RevisionResult(
                id=sha,
                author=author,
                committer=committer,
                author_date=author_date,
                committer_date=committer_date,
                message=message,
            )
