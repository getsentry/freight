from __future__ import absolute_import

from freight.config import db, queue
from freight.models import App, Task
from freight.testutils import TestCase


class DeleteObjectTest(TestCase):
    def test_delete_app(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)

        queue.apply('freight.jobs.delete_object', kwargs={
            'model': 'App',
            'object_id': app.id,
        })

        db.session.expire_all()

        assert Task.query.filter(Task.app_id == app.id).count() == 0
        assert not App.query.get(app.id)
