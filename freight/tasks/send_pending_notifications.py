from __future__ import absolute_import

import logging

from freight import notifiers
from freight.config import celery, redis
from freight.models import Task
from freight.notifiers import queue
from freight.utils.redis import lock


@celery.task(name='freight.send_pending_notifications', max_retries=None)
def send_pending_notifications():
    while True:
        with lock(redis, 'notificationcheck', timeout=5):
            data = queue.get()

        if data is None:
            logging.info('No due notifications found')
            return

        task = Task.query.get(data['task'])
        if task is None:
            logging.error('Task not found for notification (id=%s)',
                          data['task'])
            continue

        notifier = notifiers.get(data['type'])
        try:
            notifier.send(
                task=task,
                config=data['config'],
                event=data['event'],
            )
        except Exception:
            logging.exception('%s notifier failed to send Task(id=%s)',
                             data['type'], task.id)
