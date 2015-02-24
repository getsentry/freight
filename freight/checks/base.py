from __future__ import absolute_import, unicode_literals

__all__ = ['Check']


class Check(object):
    def get_default_options(self):
        return {
        }

    def get_options(self):
        return {}

    def check(self, app, sha, config):
        raise NotImplementedError
