import json

from freight.config import db
from freight.models import TaskStatus
from freight.testutils import TestCase


class DeployDetailsBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(app=self.app, user=self.user)
        self.deploy = self.create_deploy(app=self.app, task=self.task)
        self.path = f"/api/0/deploys/{self.deploy.id}/"
        self.alt_path = f"/api/0/deploys/{self.app.name}/{self.deploy.environment}/{self.deploy.number}/"
        super().setUp()


class DeployDetailsTest(DeployDetailsBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.deploy.id)

    def test_alt_path(self):
        resp = self.client.get(self.alt_path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.deploy.id)


class DeployUpdateTest(DeployDetailsBase):
    def test_simple(self):
        resp = self.client.put(self.path, data={"status": "cancelled"})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.deploy.id)
        db.session.expire(self.task)
        db.session.refresh(self.task)
        assert self.task.status == TaskStatus.cancelled

    def test_alt_path(self):
        resp = self.client.put(self.alt_path, data={"status": "cancelled"})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == str(self.deploy.id)
        db.session.expire(self.task)
        db.session.refresh(self.task)
        assert self.task.status == TaskStatus.cancelled
