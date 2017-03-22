from __future__ import absolute_import

__all__ = ['Hook']


class Hook(object):
    def deploy(self, app, env):
        raise NotImplementedError
