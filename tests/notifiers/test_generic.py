import json
import responses

from freight import notifiers
from freight.notifiers import NotifierEvent
from freight.models import TaskStatus
from freight.testutils import TestCase


class GenericNotifierBase(TestCase):
    def setUp(self):
        self.notifier = notifiers.get("Generic")
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(
            app=self.app, user=self.user, status=TaskStatus.finished
        )
        self.deploy = self.create_deploy(app=self.app, task=self.task)


class GenericNotifierTest(GenericNotifierBase):
    @responses.activate
    def test_send_finished_task(self):
        responses.add(responses.POST, "http://example.com/")

        config = {"webhook_url": "http://example.com/"}

        self.notifier.send_deploy(
            self.deploy, self.task, config, NotifierEvent.TASK_FINISHED
        )

        call = responses.calls[0]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "http://example.com/"
        body = responses.calls[0].request.body
        payload = json.loads(body)
        print(payload)
        assert payload

    @responses.activate
    def test_send_started_task(self):
        responses.add(responses.POST, "http://example.com/")

        config = {"webhook_url": "http://example.com/"}

        self.notifier.send_deploy(
            self.deploy, self.task, config, NotifierEvent.TASK_STARTED
        )

        call = responses.calls[0]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "http://example.com/"
        body = responses.calls[0].request.body
        payload = json.loads(body)
        print(payload)
        assert payload
