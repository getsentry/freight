import json

from freight.config import db
from freight.models import LogChunk
from freight.testutils import TestCase


class DeployLogBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(app=self.app, user=self.user)
        self.deploy = self.create_deploy(app=self.app, task=self.task)
        self.path = f"/api/0/deploys/{self.deploy.id}/log/"
        self.alt_path = f"/api/0/deploys/{self.app.name}/{self.deploy.environment}/{self.deploy.number}/log/"

        offset = 0
        for char in "hello world":
            db.session.add(
                LogChunk(task_id=self.task.id, text=char, size=len(char), offset=offset)
            )
            offset += len(char)
        db.session.commit()

        super().setUp()


class DeployLogTest(DeployLogBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["nextOffset"] == 11
        assert "".join(chunk["text"] for chunk in data["chunks"]) == "hello world"

    def test_alt_path(self):
        resp = self.client.get(self.alt_path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["nextOffset"] == 11
        assert "".join(chunk["text"] for chunk in data["chunks"]) == "hello world"

    def test_limit_and_offset(self):
        resp = self.client.get(self.path + "?limit=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["chunks"][0]["text"] == "h"
        assert data["nextOffset"] == 1

        resp = self.client.get(self.path + "?limit=1&offset=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["chunks"][0]["text"] == "e"
        assert data["nextOffset"] == 2

    def test_tail(self):
        resp = self.client.get(self.path + "?offset=-1&limit=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["chunks"][0]["text"] == "d"
        assert data["nextOffset"] == 11

        resp = self.client.get(self.path + "?offset=-1&limit=11")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "".join(chunk["text"] for chunk in data["chunks"]) == "hello world"
        assert data["nextOffset"] == 11
