from __future__ import absolute_import

import logging

from freight.config import celery, db, redis
from freight.models import App, Task, TaskStatus
from freight.utils.redis import lock


def has_active_task(app_id, env):
    return db.session.query(
        Task.query.filter(
            Task.status == TaskStatus.in_progress,
            Task.app_id == app_id,
            Task.environment == env,
        ).exists(),
    ).scalar()


def get_pending_task_id(app_id, env):
    return db.session.query(
        Task.id,
    ).filter(
        Task.status == TaskStatus.pending,
        Task.app_id == app_id,
        Task.environment == env,
    ).order_by(
        Task.date_created.asc(),
    ).limit(1).scalar()


@celery.task(name='freight.check_queue', max_retries=None)
def check_queue():
    """
    Checks the pending task queue and, given there's not an in-progress task
    for the given APP + ENV, marks the latest as in progress and fires the
    execute_task job.
    """
    pending_queues = list(db.session.query(
        Task.app_id, Task.environment
    ).filter(
        Task.status == TaskStatus.pending
    ).group_by(
        Task.app_id, Task.environment
    ))
    logging.info('Found pending tasks for %d queues', len(pending_queues))

    for app_id, environment in pending_queues:
        app = App.query.get(app_id)
        with lock(redis, 'taskcheck:{}-{}'.format(app.id, environment), timeout=5):
            if has_active_task(app.id, environment):
                logging.info('Task already in progress for %s/%s', app.name, environment)
                continue

            task_id = get_pending_task_id(app.id, environment)
            if not task_id:
                logging.info('Unable to find a pending task for %s/%s', app.name, environment)
                continue

            Task.query.filter(
                Task.id == task_id
            ).update({
                'status': TaskStatus.in_progress,
            }, synchronize_session=False)

            celery.send_task("freight.execute_task", [task_id])
