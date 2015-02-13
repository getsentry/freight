from __future__ import absolute_import, unicode_literals

import logging
import os

from datetime import datetime
from flask import current_app

from ds import providers, vcs
from ds.config import celery, db
from ds.models import App, LogChunk, Repository, Task, TaskStatus
from ds.utils.workspace import Workspace


@celery.task(name='ds.execute_task', max_retries=None)
def execute_task(task_id):
    task = Task.query.filter(
        Task.id == task_id
    ).first()
    if not task:
        logging.warn('Received ExecuteTask with missing Task(id=%s)', task_id)
        return

    app = App.query.filter(App.id == task.app_id).first()
    repo = Repository.query.filter(Repository.id == app.repository_id).first()

    task.date_started = datetime.utcnow()
    db.session.add(task)
    db.session.commit()

    provider = providers.get(task.provider)

    LogChunk.query.filter(LogChunk.task_id == task.id).delete()

    log_offset = [0]

    def save_log_chunk(text):
        db.session.add(LogChunk(
            task_id=task_id,
            text=text,
            offset=log_offset[0],
            size=len(text),
        ))
        db.session.commit()
        log_offset[0] += len(text)

    workspace = Workspace(
        path=os.path.join(
            current_app.config['WORKSPACE_ROOT'], 'ds-repo-{}'.format(repo.id)
        ),
        on_log_chunk=save_log_chunk,
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
    vcs_backend.checkout(task.ref)

    try:
        provider.execute(workspace, task)
    except Exception as exc:
        current_app.logger.exception(unicode(exc))
        task.status = TaskStatus.failed
    else:
        task.status = TaskStatus.finished
    task.date_finished = datetime.utcnow()
    db.session.add(task)
