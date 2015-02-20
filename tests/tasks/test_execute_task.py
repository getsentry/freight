from __future__ import absolute_import, unicode_literals

from ds import vcs
from ds.config import celery, db
from ds.models import LogChunk, TaskStatus
from ds.testutils import TransactionTestCase
from ds.utils.workspace import Workspace


class ExecuteTaskTestCase(TransactionTestCase):
    # TODO(dcramer): this test relies on quite a few things actually working
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)
        db.session.commit()

        workspace = Workspace(
            path=repo.get_path(),
        )

        vcs_backend = vcs.get(
            repo.vcs,
            url=repo.url,
            workspace=workspace,
        )

        if vcs_backend.exists():
            vcs_backend.update()
        else:
            vcs_backend.clone()

        celery.apply("ds.execute_task", task_id=task.id)
        # celery.send_task("ds.execute_task", [task.id])

        db.session.expire_all()

        assert task.date_started is not None
        assert task.date_finished is not None
        assert task.status == TaskStatus.finished

        logchunks = list(LogChunk.query.filter(
            LogChunk.task_id == task.id,
        ).order_by(LogChunk.offset.asc()))

        assert len(logchunks) >= 1
        all_text = ''.join(c.text for c in logchunks)
        assert ">> Running ['/bin/echo', 'helloworld']\n" in all_text
