from __future__ import absolute_import

from tempfile import NamedTemporaryFile


class LogBuffer(object):
    def __init__(self, chunk_size=4096):
        self.chunk_size = chunk_size
        self.fp = NamedTemporaryFile()

    def fileno(self):
        return self.fp.fileno()

    def write(self, chunk):
        self.fp.write(chunk)
        self.fp.flush()

    def close(self, force=False):
        if force:
            self.fp.close()

    def flush(self):
        self.fp.flush()

    def iter_chunks(self):
        self.flush()

        chunk_size = self.chunk_size
        result = ''
        offset = 0
        with open(self.fp.name) as fp:
            for chunk in fp:
                result += chunk
                while len(result) >= chunk_size:
                    newline_pos = result.rfind('\n', 0, chunk_size)
                    if newline_pos == -1:
                        newline_pos = chunk_size
                    else:
                        newline_pos += 1
                    yield (offset, result[:newline_pos])
                    offset += newline_pos
                    result = result[newline_pos:]
            if result:
                yield(offset, result)

        self.close(True)
