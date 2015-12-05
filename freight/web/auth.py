from __future__ import absolute_import

import logging

from flask import current_app, redirect, request, session, url_for, abort
from flask.views import MethodView
from oauth2client.client import FlowExchangeError

from freight.auth import AccessDeniedError
from freight.config import db
from freight.models import User


GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

GITHUB_AUTH_URI = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URI = 'https://github.com/login/oauth/access_token'
GITHUB_API_USER_URI = 'https://api.github.com/user'
GITHUB_API_USER_TEAMS_URI = 'https://api.github.com/user/teams'


logger = logging.getLogger(__name__)


class LoginView(MethodView):
    def __init__(self, authorized_url):
        self.authorized_url = authorized_url
        super(LoginView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        provider = current_app.state['auth_provider']
        auth_uri = provider.step1_get_authorize_url(redirect_uri=redirect_uri)
        return redirect(auth_uri)


class AuthorizedView(MethodView):
    def __init__(self, complete_url, authorized_url):
        self.complete_url = complete_url
        self.authorized_url = authorized_url
        super(AuthorizedView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        provider = current_app.state['auth_provider']

        try:
            resp = provider.step2_exchange(request.args['code'], redirect_uri)
        except FlowExchangeError as e:
            # If the flow breaks, one likely condition is that we've been given
            # an expired code for the exchange. Redirect the user to the
            # authentication provider again.
            logger.warning('OAuth 2.0 code exchange failed: %s '
                           '(redirect URI: %s)' % (e, redirect_uri))
            return redirect(provider.step1_get_authorize_url(redirect_uri))
        except AccessDeniedError:
            # If access denied, abort with a 403 Forbidden.
            logger.info('access denied for OAuth 2.0 authorization')
            abort(403)

        user = User.query.filter(
            User.name == resp.id_token['email'],
        ).first()
        if user is None:
            user = User(name=resp.id_token['email'])
            db.session.add(user)
            db.session.flush()

        session['uid'] = user.id
        session['access_token'] = resp.access_token
        session['email'] = resp.id_token['email']

        return redirect(url_for(self.complete_url))


class LogoutView(MethodView):
    def __init__(self, complete_url):
        self.complete_url = complete_url
        super(LogoutView, self).__init__()

    def get(self):
        session.pop('uid', None)
        session.pop('access_token', None)
        session.pop('email', None)
        return redirect(url_for(self.complete_url))
