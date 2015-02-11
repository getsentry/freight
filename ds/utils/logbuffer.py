from __future__ import absolute_import

from tempfile import NamedTemporaryFile


class LogBuffer(object):
    def __init__(self, chunk_size=4096):
        self.chunk_size = chunk_size
        self.fp = NamedTemporaryFile()

    def __iter__(self):
        chunk_size = self.chunk_size
        result = ''
        offset = 0
        self.seek(0)
        for chunk in self.fp:
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
        if result:
            yield result

    def fileno(self):
        return self.fp.fileno()

    def write(self, chunk):
        self.fp.write(chunk)
        self.fp.flush()

    def close(self):
        self.fp.close()

    def flush(self):
        self.fp.flush()

    def seek(self, offset):
        self.fp.seek(offset)
