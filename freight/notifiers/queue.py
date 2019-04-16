import json

from time import time

from freight.config import redis


class NotificationQueue(object):
    delay = 5000  # ms
    prefix = "notif"
    conn = redis

    def __init__(self, conn=None, prefix=None, delay=None):
        if conn is not None:
            self.conn = conn
        if prefix is not None:
            self.prefix = prefix
        if delay is not None:
            self.delay = delay

    def put(self, task, type, config, event):
        key = f"{self.prefix}:data:{type}:{task.id}"
        pipe = self.conn.pipeline()
        # the score represents the time enqueued, thus the debounce time
        # can be controlled after the fact
        pipe.zadd(f"{self.prefix}:queue", {key: time()})
        pipe.hmset(
            key,
            {
                "task": int(task.id),
                "type": type,
                "config": json.dumps(config),
                "event": event,
            },
        )
        pipe.execute()

    def remove(self, task, type):
        key = f"{self.prefix}:data:{type}:{task.id}"
        pipe = self.conn.pipeline()
        # the score represents the time enqueued, thus the debounce time
        # can be controlled after the fact
        pipe.zrem(f"{self.prefix}:queue", key)
        pipe.rem(key)
        pipe.execute()

    def get(self):
        """
        Fetches and removes a due item from the queue.

        If no pending items are available, returns None.
        """
        queue_key = f"{self.prefix}:queue"
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
        data = decode_response(pipe.execute()[0])
        data["config"] = json.loads(data["config"])
        data["event"] = int(data["event"])
        return data


def decode_response(data):
    rv = {}
    for k, v in data.items():
        k = k.decode("utf8")
        if isinstance(v, bytes):
            v = v.decode("utf8")
        rv[k] = v
    return rv
