from __future__ import absolute_import, unicode_literals

__all__ = ['TestCase']

import unittest

from flask import current_app

from .client import AuthenticatedTestClient
from .fixtures import Fixtures


class TestCase(unittest.TestCase, Fixtures):
    def setUp(self):
        self.client = AuthenticatedTestClient(
            current_app, current_app.response_class
        )
        super(TestCase, self).setUp()
