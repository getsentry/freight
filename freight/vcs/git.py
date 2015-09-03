from __future__ import absolute_import

__all__ = ['GitVcs']

import os

from urlparse import urlparse

from .base import Vcs, CommandError, UnknownRevision


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
            if e.stderr and 'unknown revision or path' in e.stderr:
                raise UnknownRevision(
                    cmd=e.cmd,
                    retcode=e.retcode,
                    stdout=e.stdout,
                    stderr=e.stderr,
                )
            raise

    def clone(self):
        self.run(['clone', '--mirror', self.remote_url, self.path])

    def update(self):
        # in case we have a non-mirror checkout, wipe it out
        if os.path.exists(os.path.join(self.workspace.path, '.git')):
            self.run(['rm', '-rf', self.workspace.path])
            self.clone()
        else:
            self.run(['fetch', '--all', '-p'])

    def checkout(self, ref, new_workspace):
        self.run(['clone', self.workspace.path, new_workspace.path],
                 workspace=new_workspace)
        self.run(['reset', '--hard', ref], workspace=new_workspace)

    def get_sha(self, ref):
        return self.run(['rev-parse', ref],
                        capture=True)
