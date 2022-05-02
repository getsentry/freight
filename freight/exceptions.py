class ApiError(Exception):
    def __init__(self, message, name=None, status_code=400):
        self.message = message
        self.name = name
        self.status_code = status_code
        super().__init__(message)


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

    def __str__(self):
        if self.stdout is not None or self.stderr is not None:
            return f"{self.cmd} failed with exit code {self.retcode}:\nSTDOUT: {repr(self.stdout)}\nSTDERR: {repr(self.stderr)}"
        return f"{self.cmd} failed with exit code {self.retcode}"


class InvalidProvider(KeyError):
    pass


class InvalidNotifier(KeyError):
    pass


class InvalidCheck(KeyError):
    pass


class InvalidHook(KeyError):
    pass
