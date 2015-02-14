from __future__ import absolute_import, unicode_literals

from ds.config import celery, db
from ds.models import App, Task
from ds.testutils import TestCase


class DeleteObjectTest(TestCase):
    def test_delete_app(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)

        celery.apply("ds.delete_object", model='App', object_id=app.id)

        db.session.expire_all()

        assert Task.query.filter(Task.app_id == app.id).count() == 0
        assert not App.query.get(app.id)
