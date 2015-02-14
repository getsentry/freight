from __future__ import absolute_import, unicode_literals

import logging

from flask import current_app
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from time import sleep, time

from ds.config import celery, db
from ds.constants import PROJECT_ROOT
from ds.models import LogChunk, Task


@celery.task(name='ds.execute_task', max_retries=None)
def execute_task(task_id):
    task = Task.query.filter(
        Task.id == task_id
    ).first()
    if not task:
        logging.warning('ExecuteTask fired with missing Task(id=%s)', task_id)
        return

    provider_config = task.provider_config

    # wipe the log incase this is a retry
    LogChunk.query.filter(
        LogChunk.task_id == task.id,
    ).delete()

    taskrunner = TaskRunner(
        task_id=task_id,
        timeout=provider_config.get('timeout', current_app.config['DEFAULT_TIMEOUT']),
    )
    taskrunner.start()
    taskrunner.wait()


class LogReporter(Thread):
    def __init__(self, app_context, task_id, process, chunk_size=4096):
        self.app_context = app_context
        self.task_id = task_id
        self.process = process
        self.chunk_size = chunk_size
        self.cur_offset = 0
        self.active = True
        Thread.__init__(self)

    def save_chunk(self, text):
        text_len = len(text)
        db.session.add(LogChunk(
            task_id=self.task_id,
            text=text,
            offset=self.cur_offset,
            size=text_len,
        ))
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
    def __init__(self, task_id, timeout=300):
        self.task_id = task_id
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
            args=['bin/run-task', str(self.task_id)],
            cwd=PROJECT_ROOT,
            stdout=PIPE,
            stderr=STDOUT
        )
        self._logthread = LogReporter(
            app_context=current_app.app_context(),
            task_id=self.task_id,
            process=self._process,
        )
        self._logthread.daemon = True
        self._logthread.start()

    def wait(self):
        assert self._process is not None, 'TaskRunner not started'
        while self.active and self._process.poll() is None:
            if self.timeout and time() > self._started + self.timeout:
                logging.error('Process exceeding time limit Task(id=%s)', self.task_id)
                self._process.terminate()
                self._logthread.terminate()
            if self._process.poll() is None:
                sleep(0.1)
        self.active = False
        return self._process.returncode
