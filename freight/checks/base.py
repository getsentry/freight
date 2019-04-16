__all__ = ["Check"]


class Check(object):
    required = False

    def get_default_options(self):
        return {}

    def get_options(self):
        return {}

    def check(self, app, sha, config):
        raise NotImplementedError
