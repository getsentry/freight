from subprocess import check_call

import pytest

from freight.testutils import TestCase
from freight.utils.workspace import Workspace
from freight.vcs.base import CommandError
from freight.vcs.git import GitVcs


class GitVcsTest(TestCase):
    root = "/tmp/freight-git-test"
    path = f"{root}/clone"
    remote_path = f"{root}/remote"
    url = f"file://{remote_path}"

    def _get_last_two_revisions(self, marker, revisions):
        if marker in revisions[0].branches:
            return revisions[0], revisions[1]
        else:
            return revisions[1], revisions[0]

    def _set_author(self, name, email):
        check_call(
            f'cd {self.remote_path} && git config --replace-all "user.name" "{name}"',
            shell=True,
        )
        check_call(
            f'cd {self.remote_path} && git config --replace-all "user.email" "{email}"',
            shell=True,
        )

    def setUp(self):
        self.reset()
        self.addCleanup(check_call, f"rm -rf {self.root}", shell=True)

    def reset(self):
        check_call(f"rm -rf {self.root}", shell=True)
        check_call(f"mkdir -p {self.path} {self.remote_path}", shell=True)
        check_call(f"git init --initial-branch=master {self.remote_path}", shell=True)
        self._set_author("Foo Bar", "foo@example.com")
        check_call(
            f'cd {self.remote_path} && touch FOO && git add FOO && git commit -m "test\nlol\n"',
            shell=True,
        )
        check_call(
            f'cd {self.remote_path} && touch BAR && git add BAR && git commit -m "biz\nbaz\n"',
            shell=True,
        )

    def get_vcs(self):
        return GitVcs(url=self.url, workspace=Workspace(self.path))

    def test_get_default_revision(self):
        vcs = self.get_vcs()
        assert vcs.get_default_revision() == "master"

    def test_simple(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        sha = vcs.get_sha("master")
        assert len(sha) == 40

    def test_get_sha_with_sha(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        sha = vcs.get_sha("master")

        assert vcs.get_sha(sha) == sha

    def test_get_sha_with_annotated_tag(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()

        # create annotated tag
        check_call(f'cd {self.remote_path} && git tag -a v1 -m "v1"', shell=True)

        vcs.update()
        master_sha = vcs.get_sha("master")
        assert len(master_sha) == 40

        check_call(
            f'cd {self.remote_path} && touch BAZ && git add BAZ && git commit -m "test\nbaz\n"',
            shell=True,
        )

        vcs.update()
        new_master_sha = vcs.get_sha("master")
        assert len(new_master_sha) == 40
        assert new_master_sha != master_sha

    def test_invalid_ref(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()
        with pytest.raises(CommandError):
            vcs.get_sha("foo")

    def test_get_sha_range(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()

        shas = vcs.get_sha_range("master", "master^")
        assert len(shas) == 1

    def test_empty_get_sha_range(self):
        vcs = self.get_vcs()
        vcs.clone()
        vcs.update()

        shas = vcs.get_sha_range("master^", "master")

        assert len(shas) == 0
