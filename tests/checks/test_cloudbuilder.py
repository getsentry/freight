import json
from textwrap import dedent

import pytest
import responses

from freight import checks
from freight.exceptions import CheckFailed, CheckPending
from freight.testutils import TestCase


class CloudbuilderCheckBase(TestCase):
    def setUp(self):
        self.check = checks.get("cloudbuilder")
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.test_project = "mycoolproject"
        self.test_sha = "0987654321"
        self.test_token = "mysuperfaketoken"


class CloudbuilderContextCheckTest(CloudbuilderCheckBase):
    @responses.activate
    def test_build_success(self):
        test_id = "successful_build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "SUCCESS",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_fail(self):
        test_id = "failed_build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "FAILURE",
                    }
                ]
            }
        )

        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        failed_log_text = """\
        LOG TEXT HERE


        THIS HERE IS A MOCK OF LOG.TEXT THAT WILL BE PRINTED


        build build build build build build steps




        MORE LOGS HERE.
        """
        build_logs = "mycoolproject.cloudbuild-logs.googleusercontent.com"
        build_id = "failed_build_id"
        responses.add(
            responses.GET,
            f"https://storage.googleapis.com/{build_logs}/log-{build_id}.txt",
            body=dedent(failed_log_text),
        )
        with pytest.raises(CheckFailed):
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_in_progress(self):
        test_id = "WIP_build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "WORKING",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckPending):
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_status_unknown(self):
        """ "STATUS_UNKNOWN": "Status of the build is unknown."""
        test_id = "unknown_build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "STATUS_UNKNOWN",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckFailed) as exception_info:
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_status_queued(self):
        """QUEUED": "Build or step is queued; work has not yet begun."""
        test_id = "build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "QUEUED",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckPending) as exception_info:
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_status_internal_error(self):
        """INTERNAL_ERROR": "Build or step failed due to an internal cause."""
        test_id = "build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "INTERNAL_ERROR",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckFailed) as exception_info:
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_status_timeout(self):
        """[summary]
            "TIMEOUT": "Build or step took longer than was allowed.",
        Arguments:
            self {[type]} -- [description]
        """
        test_id = "build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "TIMEOUT",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckFailed) as exception_info:
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_status_cancelled(self):
        """[summary]
        "CANCELLED": "Build or step was canceled by a user.",
        """
        test_id = "build_id"
        body = json.dumps(
            {
                "builds": [
                    {
                        "id": test_id,
                        "logUrl": f"https://console.cloud.google.com/gcr/builds/{test_id}?project={self.test_project}",
                        "logsBucket": f"gs://{self.test_project}.cloudbuild-logs.googleusercontent.com",
                        "status": "CANCELLED",
                    }
                ]
            }
        )
        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            body=body,
        )

        config = {"project": self.test_project, "oauth_token": self.test_token}

        with pytest.raises(CheckFailed) as exception_info:
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_missing_body(self):
        config = {"project": self.test_project, "oauth_token": self.test_token}

        responses.add(
            responses.GET,
            f"https://cloudbuild.googleapis.com/v1/projects/{self.test_project}/builds",
            status=400,
        )

        with pytest.raises(CheckFailed):
            self.check.check(self.app, self.test_sha, config)
