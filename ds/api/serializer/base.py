from __future__ import absolute_import, unicode_literals

__all__ = ['Serializer']


class Serializer(object):
    def __call__(self, *args, **kwargs):
        return self.serialize(*args, **kwargs)

    def get_attrs(self, item_list):
        return {}

    def serialize(self, item, attrs):
        return {}

    def format_datetime(self, datetime):
        if not datetime:
            return
        return datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
