from __future__ import absolute_import, unicode_literals

import freight
import sys

from flask import current_app, redirect, request, session, url_for
from flask.views import MethodView
from oauth2client.client import OAuth2WebServerFlow

from freight.config import db
from freight.models import User

GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


def get_auth_flow(redirect_uri=None):
    # XXX(dcramer): we have to generate this each request because oauth2client
    # doesn't want you to set redirect_uri as part of the request, which causes
    # a lot of runtime issues.
    auth_uri = GOOGLE_AUTH_URI
    if current_app.config['GOOGLE_DOMAIN']:
        auth_uri = auth_uri + '?hd=' + current_app.config['GOOGLE_DOMAIN']

    return OAuth2WebServerFlow(
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=redirect_uri,
        user_agent='ds/{0} (python {1})'.format(
            freight.VERSION,
            sys.version,
        ),
        auth_uri=auth_uri,
        token_uri=GOOGLE_TOKEN_URI,
        revoke_uri=GOOGLE_REVOKE_URI,
    )


class LoginView(MethodView):
    def __init__(self, authorized_url):
        self.authorized_url = authorized_url
        super(LoginView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri)
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


class AuthorizedView(MethodView):
    def __init__(self, complete_url, authorized_url):
        self.complete_url = complete_url
        self.authorized_url = authorized_url
        super(AuthorizedView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri)
        resp = flow.step2_exchange(request.args['code'])

        if current_app.config['GOOGLE_DOMAIN']:
            if resp.id_token.get('hd') != current_app.config['GOOGLE_DOMAIN']:
                # TODO(dcramer): this should show some kind of error
                return redirect(url_for(self.complete_url))

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
