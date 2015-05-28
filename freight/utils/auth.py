from __future__ import absolute_import

from flask import request, session

from freight.models import User

NOT_SET = object()


def get_current_user():
    """
    Return the currently authenticated user based on their active session.
    """
    if getattr(request, 'current_user', NOT_SET) is NOT_SET:
        if session.get('uid') is None:
            request.current_user = None
        else:
            request.current_user = User.query.get(session['uid'])
            if request.current_user is None:
                del session['uid']
    return request.current_user
