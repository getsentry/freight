import json
from unittest import mock

from freight.models import App
from freight.testutils import TestCase


class AppDetailsBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.path = f"/api/0/apps/{self.app.name}/"
        super().setUp()


class AppDetailsTest(AppDetailsBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.app.id)


class AppUpdateTest(AppDetailsBase):
    def test_simple(self):
        resp = self.client.put(
            self.path,
            data={
                "name": "foobar",
                "provider": "shell",
                "providerConfig": '{"command": "/usr/bin/true", "timeout": 50}',
                "notifiers": '[{"type": "slack", "config": {"webhook_url": "https://example.com"}},{"type": "datadog", "config": {"webhook_url": "https://example.com"}}]',
                "checks": '[{"type": "github-apps", "config": {"contexts": ["travisci"], "repo": "getsentry/freight"}}]',
                "repository": "git@example.com:repo-name.git",
                "environments": '{"staging": {"default_ref": "develop"}}',
            },
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.app.id)

        app = App.query.get(self.app.id)
        deploy_config = app.deploy_config
        assert app.name == "foobar"
        assert deploy_config.provider == "shell"
        assert deploy_config.provider_config["command"] == "/usr/bin/true"
        assert deploy_config.provider_config["timeout"] == 50
        assert deploy_config.notifiers == [
            {"type": "slack", "config": {"webhook_url": "https://example.com"}},
            {"type": "datadog", "config": {"webhook_url": "https://example.com"}},
        ]

        assert len(deploy_config.checks) == 1
        assert deploy_config.checks[0]["type"] == "github-apps"
        assert deploy_config.checks[0]["config"] == {
            "contexts": ["travisci"],
            "repo": "getsentry/freight",
        }
        assert len(app.environments) == 1
        assert app.environments["staging"] == {"default_ref": "develop"}

    def test_no_params(self):
        resp = self.client.put(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.app.id)

        app = App.query.get(self.app.id)
        deploy_config = app.deploy_config
        assert app.name == self.app.name
        assert deploy_config.provider == self.deploy_config.provider
        assert deploy_config.provider_config == self.deploy_config.provider_config

    def test_invalid_provider(self):
        resp = self.client.put(self.path, data={"provider": "invalid"})
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_provider"

    def test_invalid_provider_config(self):
        resp = self.client.put(
            self.path, data={"provider": "shell", "providerConfig": "{}"}
        )
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_provider"

    def test_invalid_notifier(self):
        resp = self.client.put(self.path, data={"notifiers": '[{"type": "invalid"}]'})
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_notifier"

    def test_invalid_notifier_config(self):
        resp = self.client.put(
            self.path,
            data={
                "notifiers": '[{"type": "slack", "config": {}},{"type": "datadog", "config": {}}]'
            },
        )
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_notifier"

    def test_invalid_check(self):
        resp = self.client.put(self.path, data={"checks": '[{"type": "invalid"}]'})
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_check"

    def test_invalid_check_config(self):
        resp = self.client.put(
            self.path, data={"checks": '[{"type": "github-apps", "config": {}}]'}
        )
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_check"

    def test_invalid_environments_type(self):
        resp = self.client.put(
            self.path, data={"environments": '[{"type": "github-apps", "config": {}}]'}
        )
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_environment"

        resp = self.client.put(self.path, data={"environments": '{"foo": []}'})
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["error_name"] == "invalid_environment"


class AppDeleteTest(AppDetailsBase):
    @mock.patch("freight.config.queue.push")
    def test_simple(self, mock_push):
        self.create_task(app=self.app, user=self.user)
        resp = self.client.delete(self.path)
        assert resp.status_code == 200

        mock_push.assert_called_once_with(
            "freight.jobs.delete_object",
            kwargs={"model": "App", "object_id": self.app.id},
        )
