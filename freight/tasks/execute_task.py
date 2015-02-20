from __future__ import absolute_import, unicode_literals

import logging
import sys

from datetime import datetime
from flask import current_app
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from time import sleep, time

from freight import notifiers
from freight.notifiers import NotifierEvent
from freight.config import celery, db
from freight.constants import PROJECT_ROOT
from freight.models import LogChunk, Task, TaskStatus


@celery.task(name='freight.execute_task', max_retries=None)
def execute_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        logging.warning('ExecuteTask fired with missing Task(id=%s)', task_id)
        return

    send_task_notifications(task, NotifierEvent.TASK_STARTED)

    provider_config = task.provider_config

    # wipe the log incase this is a retry
    LogChunk.query.filter(
        LogChunk.task_id == task.id,
    ).delete()

    taskrunner = TaskRunner(
        task=task,
        timeout=provider_config.get('timeout', current_app.config['DEFAULT_TIMEOUT']),
    )
    taskrunner.start()
    taskrunner.wait()

    # reload the task from the database due to subprocess changes
    db.session.expire(task)
    db.session.refresh(task)

    if task.status in (TaskStatus.pending, TaskStatus.in_progress):
        logging.error('Task(id=%s) did not finish cleanly', task.id)
        task.status = TaskStatus.failed
        task.date_finished = datetime.utcnow()
        db.session.add(task)
        db.session.commit()

    send_task_notifications(task, NotifierEvent.TASK_FINISHED)


def send_task_notifications(task, event):
    for data in task.notifiers:
        notifier = notifiers.get(data['type'])
        config = data.get('config', {})
        if not notifier.should_send(task, config, event):
            continue

        try:
            notifier.send(task, config, event)
        except Exception as exc:
            logging.exception('%s notifier failed to send Task(id=%s)', data['type'], task.id)


class LogReporter(Thread):
    def __init__(self, app_context, task_id, process, chunk_size=4096):
        self.app_context = app_context
        self.task_id = task_id
        self.process = process
        self.chunk_size = chunk_size
        self.cur_offset = 0
        self.active = True
        Thread.__init__(self)
        self.daemon = True

    def save_chunk(self, text):
        # we also want to pipe this to stdout
        sys.stdout.write(text)

        text_len = len(text)
        db.session.add(LogChunk(
            task_id=self.task_id,
            text=text,
            offset=self.cur_offset,
            size=text_len,
        ))

        # we commit immediately to ensure the API can stream logs
        db.session.commit()
        self.cur_offset += text_len

    def terminate(self):
        self.active = False

    def run(self):
        with self.app_context:
            self._run()

    def _run(self):
        chunk_size = self.chunk_size
        proc = self.process
        result = ''

        while self.active:
            is_running = proc.poll() is None
            chunk = proc.stdout.read(1)
            if not (is_running or chunk):
                break

            while self.active and chunk:
                result += chunk
                while len(result) >= chunk_size:
                    newline_pos = result.rfind('\n', 0, chunk_size)
                    if newline_pos == -1:
                        newline_pos = chunk_size
                    else:
                        newline_pos += 1
                    self.save_chunk(result[:newline_pos])
                    result = result[newline_pos:]
                chunk = proc.stdout.read(1)
            sleep(0.1)

        if result:
            self.save_chunk(result)


class TaskRunner(object):
    def __init__(self, task, timeout=300):
        self.task = task
        self.timeout = timeout
        self.active = False
        self._logthread = None
        self._process = None
        self._started = None

    def start(self):
        # TODO(dcramer): we should probably move the log capture up to this
        # level so we *always* get full/correct logs
        assert not self.active, 'TaskRunner already started'
        self.active = True
        self._started = time()
        self._process = Popen(
            args=['bin/run-task', str(self.task.id)],
            cwd=PROJECT_ROOT,
            stdout=PIPE,
            stderr=STDOUT
        )
        self._logreporter = LogReporter(
            app_context=current_app.app_context(),
            task_id=self.task.id,
            process=self._process,
        )
        self._logreporter.start()

    def _timeout(self):
        logging.error('Task(id=%s) exceeded time limit of %ds', self.task.id, self.timeout)

        self._process.terminate()
        self._logreporter.terminate()

        self._logreporter.save_chunk('Process exceeded time limit of %ds\n' % self.timeout)

        # TODO(dcramer): ideally we could just send the signal to the subprocess
        # so it can still manage the failure state
        self.task.status = TaskStatus.failed
        self.task.date_finished = datetime.utcnow()
        db.session.add(self.task)
        db.session.commit()

    def _cancel(self):
        logging.error('Task(id=%s) was cancelled', self.task.id)

        self._process.terminate()
        self._logreporter.terminate()

        self._logreporter.save_chunk('Task was cancelled\n')

        # TODO(dcramer): ideally we could just send the signal to the subprocess
        # so it can still manage the failure state
        self.task.date_finished = datetime.utcnow()
        db.session.add(self.task)
        db.session.commit()

    def _is_cancelled(self):
        cur_status = db.session.query(
            Task.status,
        ).filter(
            Task.id == self.task.id,
        ).scalar()
        return cur_status == TaskStatus.cancelled

    def wait(self):
        assert self._process is not None, 'TaskRunner not started'
        while self.active and self._process.poll() is None:
            if self.timeout and time() > self._started + self.timeout:
                self._timeout()
            if self._is_cancelled():
                self._cancel()
            if self._process.poll() is None:
                sleep(0.1)
        self.active = False
        self._logreporter.join()
        return self._process.returncode
