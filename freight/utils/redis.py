from __future__ import absolute_import

from contextlib import contextmanager
from flask import current_app
from random import random
from time import sleep


class UnableToGetLock(Exception):
    pass


@contextmanager
def lock(conn, lock_key, timeout=3, expire=None, nowait=False):
    if expire is None:
        expire = timeout

    delay = 0.01 + random() / 10
    attempt = 0
    max_attempts = timeout / delay
    got_lock = None
    while not got_lock and attempt < max_attempts:
        pipe = conn.pipeline()
        pipe.setnx(lock_key, '')
        pipe.expire(lock_key, expire)
        got_lock = pipe.execute()[0]
        if not got_lock:
            if nowait:
                break
            sleep(delay)
            attempt += 1

    current_app.logger.debug('Acquiring lock on %s', lock_key)

    if not got_lock:
        raise UnableToGetLock('Unable to fetch lock on %s' % (lock_key,))

    try:
        yield
    finally:
        current_app.logger.debug('Releasing lock on %s', lock_key)

        try:
            conn.delete(lock_key)
        except Exception as e:
            current_app.logger.exception(e)
