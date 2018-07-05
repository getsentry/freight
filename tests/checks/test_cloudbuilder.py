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
        body = json.dumps([
            {
                "builds":[
                    {
                        "id":"thisisabuildid",
                        "logUrl":"https://console.cloud.google.com/gcr/builds/thisisabuildid?project=mycoolproject",
                        "logsBucket":"gs://mycoolproject.cloudbuild-logs.googleusercontent.com",
                        "status":"SUCCESS",
                    },
                ]
            }
        ])

        responses.add(responses.GET, 'https://api.github.com/repos/getsentry/freight/commits/{}/statuses'.format("abcdefg"),
                      body=body)

        config = {'contexts': ['travisci'], 'repo': 'getsentry/freight'}

        self.check.check(self.app, 'abcdefg', config)

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
