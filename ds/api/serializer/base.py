from __future__ import absolute_import


registry = {}


def serialize(value):
    if not value:
        return value
    elif not isinstance(value, (list, tuple)):
        return serialize([value])[0]

    # elif isinstance(obj, dict):
    #     return dict((k, serialize(v, request=request)) for k, v in obj.iteritems())
    try:
        serializer = registry[type(value[0])]
    except KeyError:
        return value

    attrs = serializer.get_attrs(item_list=value)
    return [serializer(o, attrs=attrs.get(o, {})) for o in value]


def register(type):
    def wrapped(cls):
        registry[type] = cls()
        return cls
    return wrapped


class Serializer(object):
    def __call__(self, *args, **kwargs):
        return self.serialize(*args, **kwargs)

    def get_attrs(self, item_list):
        return {}

    def serialize(self, item, attrs):
        return {}
