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
                u'builds': [
                    {
                        u'buildTriggerId':u'a83e295b-8dbc-4b45-b430-50f94e78a27b',
                        u'id':u'e6fc46d0-f0e3-4fe4-9134-ca6c8b3111f2',
                        u'logUrl':            u'https://console.cloud.google.com/gcr/builds/e6fc46d0-f0e3-4fe4-9134-ca6c8b3111f2?project=294472738882',
                        u'logsBucket':            u'gs://294472738882.cloudbuild-logs.googleusercontent.com',
                        u'status':u'SUCCESS',
                    },
                ]
            }
        ])

        responses.add(responses.GET, 'https://api.github.com/repos/getsentry/freight/commits/{}/statuses'.format(sha),
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
