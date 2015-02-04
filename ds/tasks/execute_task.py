from __future__ import absolute_import

import logging
import os

from flask import current_app

from ds import providers, vcs
from ds.config import celery
from ds.models import App, Repository, Task
from ds.utils.workspace import Workspace


def get_vcs_backend(repo):
    kwargs = {
        'path': os.path.join(current_app.config['REPO_ROOT'], str(repo.id)),
        'url': repo.url,
    }
    return vcs.get(repo.vcs, **kwargs)


@celery.task(name='ds.execute_task')
def execute_task(task_id):
    task = Task.query.filter(
        Task.id == task_id
    ).first()
    if not task:
        logging.warn('Received execute_task with missing Task(id=%s)', task_id)
        return

    app = App.query.filter(App.id == task.app_id).first()
    repo = Repository.query.filter(Repository.id == app.repository_id).first()

    provider = providers.get(task.provider)
    vcs = get_vcs_backend(repo)

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()
    vcs.checkout(task.ref)

    workspace = Workspace(vcs.path)
    provider.execute_task(workspace, task)
