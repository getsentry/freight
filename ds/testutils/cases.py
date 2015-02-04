from __future__ import absolute_import

__all__ = ['TestCase']

import unittest

from flask import current_app as app

from .fixtures import Fixtures


class TestCase(unittest.TestCase, Fixtures):
    def setUp(self):
        # mock out mail
        self.client = app.test_client()
        super(TestCase, self).setUp()
