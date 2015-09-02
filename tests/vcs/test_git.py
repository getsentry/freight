from __future__ import absolute_import

from subprocess import check_call

from freight.testutils import TestCase
from freight.utils.workspace import Workspace
from freight.vcs.git import GitVcs


class GitVcsTest(TestCase):
    root = '/tmp/freight-git-test'
    path = '%s/clone' % (root,)
    remote_path = '%s/remote' % (root,)
    url = 'file://%s' % (remote_path,)

    def _get_last_two_revisions(self, marker, revisions):
        if marker in revisions[0].branches:
            return revisions[0], revisions[1]
        else:
            return revisions[1], revisions[0]

    def _set_author(self, name, email):
        check_call('cd {0} && git config --replace-all "user.name" "{1}"'
                   .format(self.remote_path, name), shell=True)
        check_call('cd {0} && git config --replace-all "user.email" "{1}"'
                   .format(self.remote_path, email), shell=True)

    def setUp(self):
        self.reset()
        self.addCleanup(check_call, 'rm -rf %s' % (self.root,), shell=True)

    def reset(self):
        check_call('rm -rf %s' % (self.root,), shell=True)
        check_call('mkdir -p %s %s' % (self.path, self.remote_path), shell=True)
        check_call('git init %s' % (self.remote_path,), shell=True)
        self._set_author('Foo Bar', 'foo@example.com')
        check_call('cd %s && touch FOO && git add FOO && git commit -m "test\nlol\n"' % (
            self.remote_path,
        ), shell=True)
        check_call('cd %s && touch BAR && git add BAR && git commit -m "biz\nbaz\n"' % (
            self.remote_path,
        ), shell=True)

    def get_vcs(self):
        return GitVcs(
            url=self.url,
            workspace=Workspace(self.path),
        )

    def test_get_default_revision(self):
        vcs = self.get_vcs()
        assert vcs.get_default_revision() == 'master'

    def test_simple(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        sha = vcs.describe('master')
        assert len(sha) == 40

    def test_get_sha(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        sha = vcs.get_sha('master')

        assert len(sha) == 40

    def test_get_sha_with_specific_sha(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()

        shas = vcs.run(['show-ref', '--hash=0'],
                       capture=True).split('\n')

        sha = vcs.get_sha(shas[0])

        assert len(sha) == 40

    def test_invalid_ref(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        assert vcs.get_sha('foo') is None
