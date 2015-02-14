from __future__ import absolute_import, unicode_literals

import json
import responses

from urlparse import parse_qs

from ds import notifiers
from ds.testutils import TestCase


class SlackNotifierBase(TestCase):
    def setUp(self):
        self.notifier = notifiers.get('slack')
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.task = self.create_task(app=self.app, user=self.user)


class SlackNotifierTest(SlackNotifierBase):
    @responses.activate
    def test_send(self):
        responses.add(responses.POST, 'http://example.com/')

        config = {'webhook_url': 'http://example.com/'}

        self.notifier.send(self.task, config)

        call = responses.calls[0]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://example.com/'
        body = parse_qs(responses.calls[0].request.body)
        payload = json.loads(body['payload'][0])
        # TODO(dcramer): we probably shouldnt hardcode this, but it'll do for now
        assert payload == {
            'attachments': [
                {'color': '#2788ce', 'fields': [
                    {'short': False, 'title': 'Details', 'value': 'Sha: master\nEnv: production'},
                ]},
            ],
            'parse': 'none',
            'text': "Task 'deploy' of 'master' unknown",
        }
