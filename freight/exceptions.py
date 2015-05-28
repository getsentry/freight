from __future__ import absolute_import


class ApiError(Exception):
    def __init__(self, message, name=None, status_code=400):
        self.message = message
        self.name = name
        self.status_code = status_code
        super(ApiError, self).__init__(message)


class CheckError(Exception):
    pass


class CheckFailed(CheckError):
    pass


class CheckPending(CheckError):
    pass


class CommandError(Exception):
    def __init__(self, cmd, retcode, stdout=None, stderr=None):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __unicode__(self):
        if self.stdout is not None or self.stderr is not None:
            return '%s failed with exit code %d:\nSTDOUT: %r\nSTDERR: %r' % (
                self.cmd, self.retcode, self.stdout, self.stderr)
        return '%s failed with exit code %d' % (self.cmd, self.retcode)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class InvalidProvider(KeyError):
    pass


class InvalidNotifier(KeyError):
    pass


class InvalidCheck(KeyError):
    pass
