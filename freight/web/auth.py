from __future__ import absolute_import

import freight
import requests

from flask import current_app, redirect, request, session, url_for, abort
from flask.views import MethodView
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError

from freight.config import db
from freight.constants import PYTHON_VERSION
from freight.models import User

GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

GITHUB_AUTH_URI = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URI = 'https://github.com/login/oauth/access_token'
GITHUB_API_USER_URI = 'https://api.github.com/user'
GITHUB_API_USER_TEAMS_URI = 'https://api.github.com/user/teams'


class GitHubOAuth2WebServerFlow(OAuth2WebServerFlow):
    """GitHub-specific OAuth 2.0 web server flow.
    """

    def step2_exchange(self, code, http=None):
        # Perform the exchange.
        resp = super(GitHubOAuth2WebServerFlow, self) \
            .step2_exchange(code, http)

        # Get the user's e-mail address, username, organization and team IDs
        # if the scopes match.
        scopes = frozenset(self.scope.split(','))
        id_token_additions = {}

        if 'user' in scopes:
            # Fetch user information.
            user_resp = requests.get(GITHUB_API_USER_URI,
                                     params={'access_token':
                                             resp.access_token})
            user_resp.raise_for_status()
            user_resp_json = user_resp.json()

            id_token_additions['email'] = user_resp_json['email']
            id_token_additions['login'] = user_resp_json['login']
            id_token_additions['id'] = user_resp_json['id']

            # Fetch teams.
            teams_resp = requests.get(GITHUB_API_USER_TEAMS_URI,
                                      params={'access_token':
                                              resp.access_token})
            teams_resp.raise_for_status()

            team_ids = set()
            organization_ids = set()

            for team in teams_resp.json():
                team_ids.add(team['id'])
                organization_ids.add(team['organization']['id'])

            id_token_additions['team_ids'] = list(team_ids)
            id_token_additions['organization_ids'] = list(organization_ids)

        if resp.id_token:
            resp.id_token.update(id_token_additions)
        else:
            resp.id_token = id_token_additions

        return resp


def get_auth_flow(redirect_uri=None):
    # Determine the flow class and arguments to use with the authentication
    # backend.
    if current_app.config['AUTH_BACKEND'] == 'github':
        return GitHubOAuth2WebServerFlow(
            client_id=current_app.config['GITHUB_CLIENT_ID'],
            client_secret=current_app.config['GITHUB_CLIENT_SECRET'],
            scope='user',
            redirect_uri=redirect_uri,
            user_agent='freight/{0} (python {1})'.format(
                freight.VERSION,
                PYTHON_VERSION,
            ),
            auth_uri=GITHUB_AUTH_URI,
            token_uri=GITHUB_TOKEN_URI
        )
    else:
        # XXX(dcramer): we have to generate this each request because
        # oauth2client doesn't want you to set redirect_uri as part of the
        # request, which causes a lot of runtime issues.
        auth_uri = GOOGLE_AUTH_URI
        if current_app.config['GOOGLE_DOMAIN']:
            auth_uri = auth_uri + '?hd=' + current_app.config['GOOGLE_DOMAIN']

        return OAuth2WebServerFlow(
            client_id=current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
            scope='https://www.googleapis.com/auth/userinfo.email',
            redirect_uri=redirect_uri,
            user_agent='freight/{0} (python {1})'.format(
                freight.VERSION,
                PYTHON_VERSION,
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
    def __init__(self, complete_url, authorized_url, login_url):
        self.complete_url = complete_url
        self.authorized_url = authorized_url
        self.login_url = login_url
        super(AuthorizedView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri)

        try:
            resp = flow.step2_exchange(request.args['code'])
        except FlowExchangeError:
            return redirect(url_for(self.login_url))

        if current_app.config['AUTH_BACKEND'] == 'google' and \
           current_app.config['GOOGLE_DOMAIN']:
            if resp.id_token.get('hd') != current_app.config['GOOGLE_DOMAIN']:
                # TODO(dcramer): this should show some kind of error
                return redirect(url_for(self.complete_url))
        elif current_app.config['AUTH_BACKEND'] == 'github':
            if current_app.config['GITHUB_TEAM_ID']:
                if current_app.config['GITHUB_TEAM_ID'] not in \
                   resp.id_token['team_ids']:
                    abort(403)
            elif current_app.config['GITHUB_ORGANIZATION_ID']:
                if current_app.config['GITHUB_ORGANIZATION_ID'] not in \
                   resp.id_token['organization_ids']:
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
