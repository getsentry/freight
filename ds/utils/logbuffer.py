from __future__ import absolute_import

import io

from tempfile import NamedTemporaryFile
from threading import Event, Condition


class LogBuffer(object):
    def __init__(self, chunk_size=4096):
        self.chunk_size = chunk_size
        self.writer = NamedTemporaryFile()
        self.reader = io.open(self.writer.name, 'rb')
        self.done = Event()
        self.cv = Condition()

    def __iter__(self):
        chunk_size = self.chunk_size
        result = ''
        offset = 0
        with self.cv:
            self.done.clear()
            chunk = ''
            while chunk or not self.done.is_set():
                self.writer.flush()
                result += chunk
                while len(result) >= chunk_size:
                    newline_pos = result.rfind('\n', 0, chunk_size)
                    if newline_pos == -1:
                        newline_pos = chunk_size
                    else:
                        newline_pos += 1
                    yield result[:newline_pos]
                    offset += newline_pos
                    result = result[newline_pos:]

                chunk = self.reader.read()
                if not chunk:
                    self.cv.wait(5)
                    chunk = self.reader.read()

            if result:
                yield result
        self.reader.close()
        self.writer.close()

    def fileno(self):
        return self.writer.fileno()

    def write(self, chunk):
        with self.cv:
            self.writer.write(chunk)
            self.writer.flush()
            self.cv.notifyAll()

    def close(self):
        with self.cv:
            self.writer.flush()
            self.done.set()
            self.cv.notifyAll()

    def flush(self):
        self.writer.flush()
