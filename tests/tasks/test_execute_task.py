from __future__ import absolute_import

from freight import vcs
from freight.config import db, queue
from freight.models import LogChunk, TaskStatus
from freight.testutils import TransactionTestCase
from freight.utils.workspace import Workspace


class ExecuteTaskTestCase(TransactionTestCase):
    # TODO(dcramer): this test relies on quite a few things actually working
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        self.create_taskconfig(app=app)
        task = self.create_task(app=app, user=user)
        deploy = self.create_deploy(app=app, task=task)
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

        queue.apply('freight.jobs.execute_deploy', kwargs={'deploy_id': deploy.id})

        db.session.expire_all()

        assert task.date_started is not None
        assert task.date_finished is not None
        assert task.status == TaskStatus.finished

        logchunks = list(LogChunk.query.filter(
            LogChunk.task_id == task.id,
        ).order_by(LogChunk.offset.asc()))

        assert len(logchunks) >= 1
        all_text = ''.join(c.text for c in logchunks)
        assert ">> Running ['/bin/echo', 'helloworld']" in all_text
