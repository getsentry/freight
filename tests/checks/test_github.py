import json
import responses
import pytest

from freight import checks
from freight.exceptions import CheckFailed, CheckPending
from freight.testutils import TestCase


class GitHubCheckBase(TestCase):
    def setUp(self):
        self.check = checks.get("github")
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)


class GitHubContextCheckTest(GitHubCheckBase):
    @responses.activate
    def test_not_passing(self):
        body = json.dumps(
            [
                {
                    "state": "failed",
                    "context": "travisci",
                    "description": "we didn't it",
                    "target_url": "example.com/build",
                }
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"contexts": ["travisci"], "repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_not_finished(self):
        body = json.dumps(
            [
                {
                    "state": "pending",
                    "context": "travisci",
                    "description": "we're doing it",
                    "target_url": "example.com/build",
                }
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"contexts": ["travisci"], "repo": "getsentry/freight"}

        with pytest.raises(CheckPending):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_missing_required_context(self):
        body = json.dumps(
            [
                {
                    "state": "success",
                    "context": "other",
                    "description": "we did it",
                    "target_url": "example.com/build",
                }
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"contexts": ["travisci"], "repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_success(self):
        body = json.dumps(
            [
                {
                    "state": "success",
                    "context": "travisci",
                    "description": "we did it",
                    "target_url": "example.com/build",
                }
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"contexts": ["travisci"], "repo": "getsentry/freight"}

        self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_no_contexts_with_none_defined(self):
        body = json.dumps([])

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_any_failing_context_with_none_define(self):
        body = json.dumps(
            [
                {
                    "state": "failing",
                    "context": "travisci",
                    "description": "we didn't do it",
                    "target_url": "example.com/build",
                }
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_partial_failed_context(self):
        body = json.dumps(
            [
                {
                    "state": "success",
                    "context": "travisci",
                    "description": "we did it",
                    "target_url": "example.com/build",
                },
                {
                    "state": "failing",
                    "context": "somethingelse",
                    "description": "we didn't do it",
                    "target_url": "example.com/build",
                },
            ]
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/statuses",
            body=body,
        )

        config = {"contexts": ["travisci"], "repo": "getsentry/freight"}

        self.check.check(self.app, "abcdefg", config)
