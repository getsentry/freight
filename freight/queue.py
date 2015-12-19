from __future__ import absolute_import

from datetime import datetime, timedelta
from functools import wraps
from redis import StrictRedis
from rq import Worker, Queue as QueueType
from time import sleep

DEFAULT_JOB_TIMEOUT = 60 * 60 * 24  # one day


def to_unix(datetime):
    return float(datetime.strftime('%s.%f'))


class Queue(object):
    def init_app(self, app, db, sentry):
        self.config = {
            'queues': app.config['QUEUES'],
            'routes': app.config['QUEUE_ROUTES'],
            'default_queue': app.config['QUEUE_DEFAULT'],
            'schedule': app.config['QUEUE_SCHEDULE'],
        }
        self.app = app
        self.db = db
        self.sentry = sentry

        self.connection = StrictRedis.from_url(
            app.config['REDIS_URL'],
            db=app.config['REDIS_DB'],
        )

    def get_queue_name(self, job_name):
        return self.config['routes'].get(job_name, self.config['default_queue'])

    def push(self, job_name, args=(), kwargs={}, **opts):
        queue = QueueType(self.get_queue_name(job_name), connection=self.connection)
        return queue.enqueue_call(
            job_name, args=args, kwargs=kwargs,
            result_ttl=0, timeout=DEFAULT_JOB_TIMEOUT, **opts
        )

    def apply(self, job_name, args=(), kwargs={}, **opts):
        """
        Run a job in-process.
        """
        queue = QueueType(self.get_queue_name(job_name), connection=self.connection, async=False)
        return queue.enqueue_call(
            job_name, args=args, kwargs=kwargs,
            result_ttl=0, timeout=DEFAULT_JOB_TIMEOUT, **opts
        )

    def job(self, *args, **kwargs):
        def wrapped(func):
            @wraps(func)
            def inner(*args, **kwargs):
                try:
                    rv = func(*args, **kwargs)
                except:
                    self.db.session.rollback()
                    raise
                else:
                    self.db.session.commit()
                    return rv
            return inner
        return wrapped

    def get_scheduler(self, interval=None):
        scheduler = Scheduler(connection=self.connection, queue=self, interval=interval)
        for job_name, job_config in self.config['schedule'].iteritems():
            scheduler.add(job_name, **job_config)
        return scheduler

    def get_worker(self, listen=()):
        if not listen:
            listen = self.config['queues']

        def send_to_sentry(job, *exc_info):
            self.sentry.captureException(
                exc_info=exc_info,
                extra={
                    'job_id': job.id,
                    'func': job.func_name,
                    'args': job.args,
                    'kwargs': job.kwargs,
                    'description': job.description,
                })

        exception_handlers = [send_to_sentry]

        return Worker(
            [
                QueueType(k, connection=self.connection)
                for k in listen
            ],
            exception_handlers=exception_handlers,
            connection=self.connection,
        )


class Scheduler(object):
    schedule_key = 'rq:schedule'

    interval = 1.0

    def __init__(self, connection, queue, interval=None):
        if interval:
            self.interval = interval
        self.connection = connection
        self.queue = queue
        self.schedule = {}

    def add(self, job_name, seconds=None):
        """
        Schedule a job to be periodically executed, at a certain interval.

        ``job_name`` is considered a unique primary key.
        """
        timestamp = datetime.utcnow() + timedelta(seconds=seconds)

        self.schedule[job_name] = {
            'seconds': seconds,
        }

        # TODO(dcramer): ideally this would use NX but redis cloud uses old
        # Redis
        self.connection.zadd(self.schedule_key, to_unix(timestamp), job_name)

    def run(self):
        while True:
            # find jobs which are scheduled in the future
            until = datetime.utcnow()
            pending = set(self.connection.zrangebyscore(
                self.schedule_key, to_unix(until), '+inf'
            ))
            for job_name, job_config in self.schedule.iteritems():
                if job_name in pending:
                    continue
                timestamp = datetime.utcnow() + timedelta(seconds=job_config['seconds'])
                self.connection.zadd(self.schedule_key, to_unix(timestamp), job_name)
                self.queue.push(job_name)
            sleep(self.interval)
