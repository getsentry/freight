from __future__ import absolute_import, unicode_literals


class ApiError(Exception):
    def __init__(self, message, name=None, status_code=400):
        self.message = message
        self.name = name
        self.status_code = status_code
        super(ApiError, self).__init__(message)


class CheckFailed(Exception):
    pass


class CommandError(Exception):
    def __init__(self, cmd, retcode, stdout=None, stderr=None):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __unicode__(self):
        return '%s returned %d:\nSTDOUT: %r\nSTDERR: %r' % (
            self.cmd, self.retcode, self.stdout, self.stderr)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class InvalidProvider(KeyError):
    pass


class InvalidNotifier(KeyError):
    pass


class InvalidCheck(KeyError):
    pass
