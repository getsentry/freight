from __future__ import absolute_import

import json
from textwrap import dedent

import pytest
import responses

from freight import checks
from freight.exceptions import CheckFailed, CheckPending
from freight.testutils import TestCase


class CloudbuilderCheckBase(TestCase):
    def setUp(self):
        self.check = checks.get('cloudbuilder')
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.test_project = "mycoolproject"
        self.test_sha = "0987654321"

class CloudbuilderContextCheckTest(CloudbuilderCheckBase):
    @responses.activate
    def test_build_success(self):
        id = "successful_build_id"
        body = json.dumps({
            "builds": [
            {
                "id": "{}".format(id),
                "logUrl":"https://console.cloud.google.com/gcr/builds/{}?project={}".format(id, self.test_project),
                "logsBucket":"gs://{}.cloudbuild-logs.googleusercontent.com".format(self.test_project),
                "status": "SUCCESS",
            },
            ]
        })
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project), body=body)

        config = {'contexts': ['cloudbuilder'], 'project': self.test_project}

        self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_fail(self):
        id = "failed_build_id"
        body = json.dumps({
            "builds": [
                {
                    "id": "{}".format(id),
                    "logUrl":"https://console.cloud.google.com/gcr/builds/{}?project={}".format(id, self.test_project),
                    "logsBucket":"gs://{}.cloudbuild-logs.googleusercontent.com".format(self.test_project),
                    "status": "Failure",
                },
            ]
        })

        responses.add(
            responses.GET,
             "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project),
             body=body
        )

        config = {'contexts': ['cloudbuilder'], 'project': self.test_project}

        with pytest.raises(CheckFailed):
            failed_log_text = """\
            LOG TEXT HERE


            THIS HERE IS A MOCK OF LOG.TEXT THAT WILL BE PRINTED


            build build build build build build steps




            MORE LOGS HERE.
            """
            responses.add(
                responses.GET,
                'https://storage.googleapis.com/{build_logs}/log-{build_id}.txt'.format(
                    build_logs="mycoolproject.cloudbuild-logs.googleusercontent.com",
                    build_id="failed_build_id"
                    ),
                body = dedent(failed_log_text)
            )
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_build_pending(self):
        body = json.dumps({
            "builds": [
            {
                "id":"thisisabuildid",
                "logUrl":"https://console.cloud.google.com/gcr/builds/thisisabuildid?project={}".format(self.test_project),
                "logsBucket":"gs://{}.cloudbuild-logs.googleusercontent.com".format(self.test_project),
                "status": "PENDING",
            },
            ]
        })
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project), body=body)

        config = {'contexts': ['cloudbuilder'], 'project': self.test_project}

        with pytest.raises(CheckPending):
            self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_missing_body(self):
        config = {'contexts': ['cloudbuilder'], 'project': self.test_project}
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project), status=400)


        with pytest.raises(Exception):
            self.check.check(self.app, self.test_sha, config)


    @responses.activate
    def test_missing_oauth(self):
        config = {
            "contexts": ['cloudbuilder'],
            "project": self.test_project,
            "oauth_token": this_token_is_fake
        }
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project))


        # with pytest.raises(Exception):
        self.check.check(self.app, self.test_sha, config)

    @responses.activate
    def test_key_error(self):
        id = "keyerror"
        body = json.dumps({
            "builds": [
            {
                "id": "{}".format(id),
                "logsBucket":"gs://{}.cloudbuild-logs.googleusercontent.com".format(self.test_project),
                "status": "SUCCESS",
            },
            ]
        })
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(self.test_project), body=body)

        config = {'contexts': ['cloudbuilder'], 'project': self.test_project}

        with pytest.raises(KeyError):
            self.check.check(self.app, self.test_sha, config)