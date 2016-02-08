from __future__ import absolute_import

import json

from time import time

from freight.config import redis


class NotificationQueue(object):
    delay = 5000  # ms
    prefix = 'notif'
    conn = redis

    def __init__(self, conn=None, prefix=None, delay=None):
        if conn is not None:
            self.conn = conn
        if prefix is not None:
            self.prefix = prefix
        if delay is not None:
            self.delay = delay

    def put(self, task, type, config, event):
        key = '{}:data:{}:{}'.format(self.prefix, type, task.id)
        pipe = self.conn.pipeline()
        # the score represents the time enqueued, thus the debounce time
        # can be controlled after the fact
        pipe.zadd('{}:queue'.format(self.prefix), key, time())
        pipe.hmset(key, {
            'task': task.id,
            'type': type,
            'config': json.dumps(config),
            'event': event,
        })
        pipe.execute()

    def remove(self, task, type):
        key = '{}:data:{}:{}'.format(self.prefix, type, task.id)
        pipe = self.conn.pipeline()
        # the score represents the time enqueued, thus the debounce time
        # can be controlled after the fact
        pipe.zrem('{}:queue'.format(self.prefix), key)
        pipe.rem(key)
        pipe.execute()

    def get(self):
        """
        Fetches and removes a due item from the queue.

        If no pending items are available, returns None.
        """
        queue_key = '{}:queue'.format(self.prefix)
        min_s = 0
        max_s = time() - (self.delay / 1000)

        results = self.conn.zrangebyscore(queue_key, min_s, max_s, 0, 1)
        if not results:
            return None

        key = results[0]
        pipe = self.conn.pipeline()
        pipe.hgetall(key)
        pipe.delete(key)
        pipe.zrem(queue_key, key)
        data = pipe.execute()[0]
        data['config'] = json.loads(data['config'])
        data['event'] = int(data['event'])
        return data
