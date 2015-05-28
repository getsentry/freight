from __future__ import absolute_import

from freight.api.serializer import serialize
from freight.testutils import TestCase


class TaskSerializerTest(TestCase):
    def test_locked(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)

        result = serialize(app)
        assert result['id'] == str(app.id)
        assert result['name'] == app.name
