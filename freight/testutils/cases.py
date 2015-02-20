from __future__ import absolute_import, unicode_literals

__all__ = ['TestCase', 'TransactionTestCase']


import pytest
import unittest

from flask import current_app
from sqlalchemy import event
from sqlalchemy.orm import Session

from freight.config import db

from .client import AuthenticatedTestClient
from .fixtures import Fixtures


class TestCase(unittest.TestCase, Fixtures):
    @pytest.fixture(autouse=True)
    def __transactions(self, request, app):
        def unregister_listener():
            event.remove(Session, "after_transaction_end", self.__restart_savepoint)

        event.listen(Session, "after_transaction_end", self.__restart_savepoint)
        request.addfinalizer(unregister_listener)

        db.session.begin_nested()
        request.addfinalizer(db.session.remove)

    def __restart_savepoint(self, session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    def setUp(self):
        self.client = AuthenticatedTestClient(
            current_app, current_app.response_class
        )
        super(TestCase, self).setUp()


class TransactionTestCase(unittest.TestCase, Fixtures):
    @pytest.fixture(autouse=True)
    def __transactions(self, request, reset_database):
        request.addfinalizer(reset_database)

    def setUp(self):
        self.client = AuthenticatedTestClient(
            current_app, current_app.response_class
        )
        super(TransactionTestCase, self).setUp()
