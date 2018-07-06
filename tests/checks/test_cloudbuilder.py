from __future__ import absolute_import

import json
import responses
import pytest

from freight import checks
from freight.exceptions import CheckFailed, CheckPending
from freight.testutils import TestCase

class CloudbuilderCheckBase(TestCase):
    def setUp(self):
        self.check = checks.get('cloudbuilder')
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)


class CloudbuilderContextCheckTest(CloudbuilderCheckBase):
    @responses.activate
    def test_success(self):
        project = "mycoolproject"
        sha = "0987654321"
        body = json.dumps({

            "builds": [
            {
                "id":"thisisabuildid",
                "logUrl":"https://console.cloud.google.com/gcr/builds/thisisabuildid?project={}".format(project),
                "logsBucket":"gs://{}.cloudbuild-logs.googleusercontent.com".format(project),
                "status": "SUCCESS",
                "context": "cloudbuilder",
                "description": "we did it",
                "target_url": "example.com/build",
            },
            ]})
        responses.add(responses.GET, "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(project), body=body)

        config = {'contexts': ['cloudbuilder'], 'project': project}

        self.check.check(self.app, sha, config)


    @responses.activate
    def test_missing_repo(self):
        pass
    
    @responses.activate
    def test_missing_oauth(self):
        pass
    
    @responses.activate
    def test_build_pending(self):
        pass
    
    @responses.activate
    def test_build_fail(self):
        pass
