import json

from collections.abc import MutableMapping

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, Unicode


class MutableDict(Mutable, MutableMapping):
    def __init__(self, value):
        self.value = value or {}

    def __setitem__(self, key, value):
        self.value[key] = value
        self.changed()

    def __delitem__(self, key):
        del self.value[key]
        self.changed()

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __repr__(self):
        return repr(self.value)

    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)

        return value


class JSONEncodedDict(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value:
            if isinstance(value, MutableDict):
                value = value.value
            return str(json.dumps(value))

        return "{}"

    def process_result_value(self, value, dialect):
        if value:
            return json.loads(value)

        return {}


MutableDict.associate_with(JSONEncodedDict)
