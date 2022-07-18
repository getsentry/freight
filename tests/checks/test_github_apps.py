import json
import responses
import pytest

from freight import checks
from freight.exceptions import CheckFailed, CheckPending
from freight.testutils import TestCase


class GitHubAppsCheckBase(TestCase):
    def setUp(self):
        self.check = checks.get("github-apps")
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)


class GitHubAppsContextCheckTest(GitHubAppsCheckBase):
    @responses.activate
    def test_not_passing(self):
        body = json.dumps(
            {
                "total_count": 1,
                "check_runs": [
                    {
                        "status": "completed",
                        "conclusion": "failure",
                        "name": "Travis CI - Branch",
                        "details_url": "https://travis/87026985",
                        "output": {"title": "Build Failed"},
                    }
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["Travis CI - Branch"], "repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_not_finished(self):
        body = json.dumps(
            {
                "total_count": 1,
                "check_runs": [
                    {
                        "status": "in_progress",
                        "name": "Travis CI - Branch",
                        "conclusion": None,
                        "details_url": "https://travis/87026985",
                        "output": {"title": "Build Failed"},
                    }
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["Travis CI - Branch"], "repo": "getsentry/freight"}

        with pytest.raises(CheckPending):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_missing_required_context(self):
        body = json.dumps(
            {
                "total_count": 1,
                "check_runs": [
                    {
                        "status": "in_progress",
                        "name": "Travis CI - Branch",
                        "conclusion": None,
                        "details_url": "https://travis/87026985",
                        "output": {"title": "Build Failed"},
                    }
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["other"], "repo": "getsentry/freight"}

        with pytest.raises(CheckPending):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_success(self):
        body = json.dumps(
            {
                "total_count": 1,
                "check_runs": [
                    {
                        "status": "completed",
                        "conclusion": "success",
                        "name": "Travis CI - Branch",
                    }
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["Travis CI - Branch"], "repo": "getsentry/freight"}

        self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_no_contexts_with_none_defined(self):
        body = json.dumps({"total_count": 0, "check_runs": []})

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_any_failing_context_with_none_define(self):
        body = json.dumps(
            {
                "total_count": 1,
                "check_runs": [
                    {
                        "status": "completed",
                        "conclusion": "failure",
                        "name": "Travis CI - Branch",
                        "details_url": "https://travis/87026985",
                        "output": {"title": "Build Failed"},
                    }
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"repo": "getsentry/freight"}

        with pytest.raises(CheckFailed):
            self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_partial_failed_context(self):
        body = json.dumps(
            {
                "total_count": 2,
                "check_runs": [
                    {
                        "status": "completed",
                        "name": "Travis CI - Branch",
                        "conclusion": "success",
                        "details_url": "https://travis/87026985",
                    },
                    {
                        "status": "completed",
                        "name": "somethingelse",
                        "conclusion": "failure",
                        "details_url": "https://travis/87026985",
                    },
                ],
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["Travis CI - Branch"], "repo": "getsentry/freight"}

        self.check.check(self.app, "abcdefg", config)

    @responses.activate
    def test_pagination(self):
        body = json.dumps(
            {
                "total_count": 150,
                "check_runs": [
                    {
                        "status": "completed",
                        "name": "somethingelse",
                        "conclusion": "failure",
                        "details_url": "https://travis/87026985",
                    },
                ]
                * 100,
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        body = json.dumps(
            {
                "total_count": 150,
                "check_runs": [
                    {
                        "status": "completed",
                        "name": "Travis CI - Branch",
                        "conclusion": "success",
                        "details_url": "https://travis/87026985",
                    },
                ]
                + [
                    {
                        "status": "completed",
                        "name": "somethingelse",
                        "conclusion": "failure",
                        "details_url": "https://travis/87026985",
                    },
                ]
                * 49,
            }
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/getsentry/freight/commits/abcdefg/check-runs",
            body=body,
        )

        config = {"contexts": ["Travis CI - Branch"], "repo": "getsentry/freight"}

        self.check.check(self.app, "abcdefg", config)
