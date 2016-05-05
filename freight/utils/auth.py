from __future__ import absolute_import

from flask import current_app, request, session

from freight.models import User

from freight.testutils.fixtures import Fixtures

NOT_SET = object()


def get_current_user():
    """
    Return the currently authenticated user based on their active session.
    Will return a dummy user if in development mode.
    """
    if getattr(request, 'current_user', NOT_SET) is NOT_SET:
        if current_app.config.get('DEV'):
            request.current_user = User.query.filter(
                User.name == 'Freight',
            ).first()
            if not request.current_user:
                request.current_user = Fixtures().create_user(
                    name='Freight',
                )

        elif session.get('uid') is None:
            request.current_user = None
        else:
            request.current_user = User.query.get(session['uid'])
            if request.current_user is None:
                del session['uid']
    return request.current_user
