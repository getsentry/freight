from __future__ import absolute_import

import logging
import os

from datetime import datetime
from flask import current_app

from ds import providers, vcs
from ds.config import celery, db
from ds.models import App, Repository, Task, TaskStatus
from ds.utils.workspace import Workspace


def get_vcs_backend(repo):
    kwargs = {
        'path': os.path.join(current_app.config['WORKSPACE_ROOT'], 'ds-repo-{}'.format(repo.id)),
        'url': repo.url,
    }
    return vcs.get(repo.vcs, **kwargs)


@celery.task(name='ds.execute_task', max_retries=None)
def run(task_id):
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
    vcs = get_vcs_backend(repo)

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()
    vcs.checkout(task.ref)

    workspace = Workspace(vcs.path)
    try:
        provider.execute_task(workspace, task)
    except Exception:
        task.status = TaskStatus.failed
    else:
        task.status = TaskStatus.finished
    task.date_finished = datetime.utcnow()
    db.session.add(task)
    db.session.commit()
