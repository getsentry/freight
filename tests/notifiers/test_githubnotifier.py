import json
import responses

from freight import notifiers
from freight.notifiers import NotifierEvent
from freight.models import TaskStatus
from freight.testutils import TestCase


class GithubNotifierBase(TestCase):
    def setUp(self):
        self.notifier = notifiers.get("github")
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(
            app=self.app, user=self.user, status=TaskStatus.finished, sha="123"
        )
        self.deploy = self.create_deploy(app=self.app, task=self.task)
        self.target_url = "http://example.com/repos/getsentry/freight/statuses/123"


class GithubNotifierTest(GithubNotifierBase):
    @responses.activate
    def test_send_finished_task(self):
        responses.add(responses.POST, self.target_url)

        config = {"api_root": "http://example.com/", "repo": "getsentry/freight"}

        self.notifier.send_deploy(
            self.deploy, self.task, config, NotifierEvent.TASK_FINISHED
        )

        call = responses.calls[0]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == self.target_url
        body = responses.calls[0].request.body
        payload = json.loads(body)
        assert payload["state"] == "success"

    @responses.activate
    def test_send_started_task(self):
        responses.add(responses.POST, self.target_url)

        config = {"api_root": "http://example.com/", "repo": "getsentry/freight"}

        self.notifier.send_deploy(
            self.deploy, self.task, config, NotifierEvent.TASK_STARTED
        )

        call = responses.calls[0]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == self.target_url
        body = responses.calls[0].request.body
        payload = json.loads(body)
        assert payload["state"] == "pending"
