from __future__ import absolute_import

import logging
import sys
import threading

from datetime import datetime
from flask import current_app
from subprocess import PIPE, Popen, STDOUT
from time import sleep, time

from freight.notifiers import NotifierEvent
from freight.notifiers.utils import send_task_notifications
from freight.config import db, queue, redis
from freight.constants import PROJECT_ROOT
from freight.models import LogChunk, Task, TaskStatus
from freight.utils.redis import lock


@queue.job()
def execute_task(task_id):
    logging.debug('ExecuteTask fired with %d active thread(s)',
                  threading.active_count())

    with lock(redis, 'task:{}'.format(task_id), timeout=5):
        task = Task.query.get(task_id)
        if not task:
            logging.warning('ExecuteTask fired with missing Task(id=%s)', task_id)
            return

        if task.status not in (TaskStatus.pending, TaskStatus.in_progress):
            logging.warning('ExecuteTask fired with finished Task(id=%s)', task_id)
            return

        task.date_started = datetime.utcnow()
        task.status = TaskStatus.in_progress
        db.session.add(task)
        db.session.commit()

    send_task_notifications(task, NotifierEvent.TASK_STARTED)

    provider_config = task.provider_config

    # wipe the log incase this is a retry
    LogChunk.query.filter(
        LogChunk.task_id == task.id,
    ).delete()

    taskrunner = TaskRunner(
        task=task,
        timeout=provider_config.get('timeout', current_app.config['DEFAULT_TIMEOUT']),
        read_timeout=provider_config.get('read_timeout', current_app.config['DEFAULT_READ_TIMEOUT']),
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


def kill_subprocess(process):
    logging.debug('Sending kill() to process %s', process.pid)
    process.kill()


def forcefully_stop_process(process, timeout=10):
    timer = threading.Timer(timeout, kill_subprocess, args=[process])
    timer.start()
    try:
        logging.debug('Sending terminate() to process %s (%ds timeout)',
                      process.pid, timeout)
        process.terminate()
        process.wait()
    finally:
        timer.cancel()


class LogReporter(threading.Thread):
    def __init__(self, app_context, task_id, process, chunk_size=4096):
        self.app_context = app_context
        self.task_id = task_id
        self.process = process
        self.chunk_size = chunk_size
        self.cur_offset = 0
        self.last_recv = None
        self.active = True
        threading.Thread.__init__(self)
        self.daemon = True
        self.write_lock = threading.Lock()

    def save_chunk(self, text):
        # we also want to pipe this to stdout
        sys.stdout.write(text)

        text = text.decode('utf-8', 'replace')
        text_len = len(text)

        with self.write_lock:
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
        self.last_recv = time()
        chunk_size = self.chunk_size
        proc = self.process
        result = ''

        while self.active:
            is_running = proc.poll() is None
            chunk = proc.stdout.read(1)
            if not (is_running or chunk):
                break

            last_write = time()
            flush_time = 3  # seconds
            while self.active and chunk:
                result += chunk
                self.last_recv = time()
                while len(result) >= chunk_size or (time() - last_write) > flush_time:
                    newline_pos = result.rfind('\n', 0, chunk_size)
                    if newline_pos == -1:
                        newline_pos = chunk_size
                    else:
                        newline_pos += 1
                    self.save_chunk(result[:newline_pos])
                    last_write = time()
                    result = result[newline_pos:]
                chunk = proc.stdout.read(1)
            sleep(0.1)

        if result:
            self.save_chunk(result)


class TaskRunner(object):
    def __init__(self, task, read_timeout=300, timeout=3600):
        self.task = task
        self.timeout = timeout
        self.read_timeout = read_timeout
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
            stderr=STDOUT,
        )
        self._logreporter = LogReporter(
            app_context=current_app.app_context(),
            task_id=self.task.id,
            process=self._process,
        )
        self._logreporter.start()

    # TODO(dcramer): currently this is the sum of checks + job time which
    # isnt ideal. We either could move checks into execute_task and have a new
    # timeout just for them, or assume this timeout includes both and likely
    # still add another timeout for checks
    def _timeout(self):
        logging.error('Task(id=%s) exceeded time limit of %ds', self.task.id, self.timeout)

        logging.debug('Sending terminate() to LogReporter')
        self._logreporter.terminate()

        forcefully_stop_process(self._process)

        self._logreporter.save_chunk('>> Process exceeded time limit of %ds\n' % self.timeout)

        with lock(redis, 'task:{}'.format(self.task.id), timeout=5):
            # TODO(dcramer): ideally we could just send the signal to the subprocess
            # so it can still manage the failure state
            self.task.status = TaskStatus.failed
            self.task.date_finished = datetime.utcnow()
            db.session.add(self.task)
            db.session.commit()

    def _read_timeout(self):
        logging.error('Task(id=%s) did not receive any updates in %ds', self.task.id, self.read_timeout)

        logging.debug('Sending terminate() to LogReporter')
        self._logreporter.terminate()

        forcefully_stop_process(self._process)

        self._logreporter.save_chunk('>> Process did not receive updates in %ds\n' % self.read_timeout)

        with lock(redis, 'task:{}'.format(self.task.id), timeout=5):
            # TODO(dcramer): ideally we could just send the signal to the subprocess
            # so it can still manage the failure state
            self.task.status = TaskStatus.failed
            self.task.date_finished = datetime.utcnow()
            db.session.add(self.task)
            db.session.commit()

    def _cancel(self):
        logging.error('Task(id=%s) was cancelled', self.task.id)

        logging.debug('Sending terminate() to LogReporter')
        self._logreporter.terminate()

        forcefully_stop_process(self._process)

        self._logreporter.save_chunk('>> Task was cancelled\n')

        with lock(redis, 'task:{}'.format(self.task.id), timeout=5):
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

    def _should_read_timeout(self):
        if not self._logreporter.last_recv:
            return False
        if not self.read_timeout:
            return False
        return self._logreporter.last_recv < time() - self.read_timeout

    def wait(self):
        assert self._process is not None, 'TaskRunner not started'
        while self.active and self._process.poll() is None:
            if self._is_cancelled():
                self._cancel()
            elif self.timeout and time() > self._started + self.timeout:
                self._timeout()
            elif self._should_read_timeout():
                self._read_timeout()
            if self._process.poll() is None:
                sleep(0.1)
        self.active = False
        logging.debug('Waiting for LogReporter to finish')
        self._logreporter.join()
        return self._process.returncode
