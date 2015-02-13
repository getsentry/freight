from __future__ import absolute_import, unicode_literals

import logging
import sys

from subprocess import Popen
from time import sleep, time

from ds.config import celery
from ds.constants import PROJECT_ROOT


@celery.task(name='ds.execute_task', max_retries=None)
def execute_task(task_id):
    taskrunner = TaskRunner(task_id)
    taskrunner.start()
    taskrunner.wait()


class TaskRunner(object):
    def __init__(self, task_id, timeout=300):
        self.task_id = task_id
        self.timeout = timeout
        self._process = None
        self._started = None

    def start(self):
        # TODO(dcramer): we should probably move the log capture up to this
        # level so we *always* get full/correct logs
        self._process = Popen(
            args=['bin/run-task', str(self.task_id)],
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd=PROJECT_ROOT,
        )
        self._started = time()

    def wait(self):
        assert self._process is not None, 'TaskRunner not started'
        while self._process.poll() is None:
            if time() > self._started + self.timeout:
                logging.error('Process exceeding time limit Task(id=%s)', self.task_id)
                self._process.terminate()
            if self._process.poll() is None:
                sleep(0.1)
        return self._process.returncode
