from __future__ import absolute_import

__all__ = ['SerializerManager']


class SerializerManager(object):
    def __init__(self):
        self.registry = {}

    def add(self, type, cls_or_none=None):
        if cls_or_none is not None:
            return self.add(type)(cls_or_none)

        def wrapped(cls):
            self.registry[type] = cls()
            return cls
        return wrapped

    def get(self, type):
        return self.registry[type]

    def serialize(self, value):
        if not value:
            return value
        elif not isinstance(value, (list, tuple)):
            return self.serialize([value])[0]

        # elif isinstance(obj, dict):
        #     return dict((k, serialize(v, request=request)) for k, v in obj.iteritems())
        try:
            serializer = self.registry[type(value[0])]
        except KeyError:
            return value

        attrs = serializer.get_attrs(item_list=value)
        return [serializer(o, attrs=attrs.get(o, {})) for o in value]

default_manager = SerializerManager()
add = default_manager.add
serialize = default_manager.serialize
