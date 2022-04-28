import logging

from freight.config import db, redis, queue
from freight.models import App, Task, Deploy, TaskStatus
from freight.utils.redis import lock


def has_active_deploy(app_id, env):
    return db.session.query(
        Deploy.query.filter(
            Task.status == TaskStatus.in_progress,
            Deploy.task_id == Task.id,
            Deploy.app_id == app_id,
            Deploy.environment == env,
        ).exists()
    ).scalar()


def get_pending_task_id(app_id, env):
    return (
        db.session.query(Task.id)
        .filter(
            Task.status == TaskStatus.pending,
            Deploy.app_id == app_id,
            Deploy.environment == env,
        )
        .order_by(Task.date_created.asc())
        .limit(1)
        .scalar()
    )


@queue.job()
def check_queue():
    """
    Checks the pending task queue and, given there's not an in-progress task
    for the given APP + ENV, marks the latest as in progress and fires the
    execute_task job.
    """
    tasks = list(
        db.session.query(Task.id, Task.app_id)
        .filter(Task.status == TaskStatus.pending)
        .group_by(Task.id, Task.app_id)
    )

    if not tasks:
        return

    logging.info("Found pending tasks for %d queues", len(tasks))

    deploys = list(
        db.session.query(Deploy.id, Deploy.app_id, Deploy.environment)
        .filter(Deploy.task_id.in_({t.id for t in tasks}))
        .group_by(Deploy.id, Deploy.app_id, Deploy.environment)
    )

    apps = {a.id: a for a in App.query.filter(App.id.in_({t.app_id for t in tasks}))}

    for deploy_id, app_id, environment in deploys:
        app = apps[app_id]
        with lock(redis, f"deploycheck:{app.id}-{environment}", timeout=5):
            if has_active_deploy(app.id, environment):
                logging.info(
                    "Deploy already in progress for %s/%s", app.name, environment
                )
                continue

            task_id = get_pending_task_id(app.id, environment)
            if not task_id:
                logging.info(
                    "Unable to find a pending deploy for %s/%s", app.name, environment
                )
                continue

            Task.query.filter(Task.id == task_id).update(
                {"status": TaskStatus.in_progress}, synchronize_session=False
            )

            queue.push("freight.jobs.execute_deploy", [deploy_id])
