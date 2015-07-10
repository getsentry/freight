import freight
import logging
import requests
import warnings

from freight.constants import PYTHON_VERSION
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError

from .exceptions import AccessDeniedError, ProviderConfigurationError


logger = logging.getLogger(__name__)


GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

GITHUB_AUTH_URI = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URI = 'https://github.com/login/oauth/access_token'
GITHUB_API_USER_URI = 'https://api.github.com/user'
GITHUB_API_USER_TEAMS_URI = 'https://api.github.com/user/teams'


class OAuth2Provider(object):
    """OAuth 2.0 provider.
    """

    def __init__(self,
                 client_id,
                 client_secret,
                 scope,
                 auth_uri,
                 token_uri,
                 revoke_uri=None):
        """Initialize an OAuth 2.0 provider.

        :param client_id: Client ID.
        :param client_secret: Client secret.
        :param scope: Scope.
        :param auth_uri: Authentication URI.
        :param token_uri: Token exchange URI.
        :param revoke_uri: Token revocation URI.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.auth_uri = auth_uri
        self.token_uri = token_uri
        self.revoke_uri = revoke_uri

    @classmethod
    def from_app_config(cls, config):
        """Instantiate provider from application configuration.

        :param config: Configuration.
        :type config: :class:`dict`
        :returns: the provider instance based on the configuration.
        :raises freight.auth.exceptions.ProviderConfigurationError:
            if the application configuration for the authentication provider
            is not valid.
        """

        raise NotImplementedError()

    def _get_flow(self, redirect_uri=None):
        """Get authorization flow.

        :param redirect_uri: Redirect URI.
        :rtype: :class:`oauth2client.client.OAuth2WebServerFlow`
        """

        return OAuth2WebServerFlow(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=redirect_uri,
            user_agent='freight/{0} (python {1})'.format(
                freight.VERSION,
                PYTHON_VERSION,
            ),
            auth_uri=self.auth_uri,
            token_uri=self.token_uri,
            revoke_uri=self.revoke_uri
        )

    def step1_get_authorize_url(self, redirect_uri=None):
        """Get provider authorize URL.

        :param redirect_uri: Optional redirect URI.
        :returns: the authorize URL For the provider to redirect the user to.
        """

        return self._get_flow(redirect_uri).step1_get_authorize_url()

    def step2_exchange(self, code, redirect_uri=None):
        """Exchange an authorization code for an access token.

        :param code: Authorization code.
        :param redirect_uri: Redirect URI.
        :returns: the exchange result.
        :rtype: :class:`oauth2client.client.OAuth2Credentials`
        :raises freight.auth.exceptions.AccessDeniedError:
            if the authenticated user does not have access by the configured
            restrictions.
        :raises oauth2client.client.FlowExchangeError:
            if an error occured during the exchange, most likely due to an
            already used code or a bad scope.
        """

        return self._get_flow(redirect_uri).step2_exchange(code)


class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth 2.0 privder.
    """

    def __init__(self,
                 client_id,
                 client_secret,
                 domain=None,
                 scope='https://www.googleapis.com/auth/userinfo.email'):
        """Initialize a Google OAuth 2.0 provider.

        :param client_id: Client ID.
        :param client_secret: Client secret.
        :param domain: Optional domain to limit authorization to.
        :param scope: Scope.
        """

        self.domain = domain

        super(GoogleOAuth2Provider, self).__init__(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            auth_uri=GOOGLE_AUTH_URI,
            token_uri=GOOGLE_TOKEN_URI,
            revoke_uri=GOOGLE_REVOKE_URI
        )

    @classmethod
    def from_app_config(cls, config):
        client_id = config.get('GOOGLE_CLIENT_ID')
        client_secret = config.get('GOOGLE_CLIENT_SECRET')
        domain = config.get('GOOGLE_TEAM_ID')

        if not client_id or not client_secret:
            raise ProviderConfigurationError(
                'Google authentication requires a client ID '
                '(GOOGLE_CLIENT_ID) and secret (GOOGLE_CLIENT_SECRET) to be '
                'provided'
            )

        if not domain:
            warnings.warn(
                'No domain provided for Google authentication (GOOGLE_DOMAIN) '
                '- any user with a Google account can authenticate'
            )

        return cls(client_id=client_id,
                   client_secret=client_secret,
                   domain=domain)

    def get_flow(self, redirect_uri=None):
        # XXX(dcramer): we have to generate this each request because
        # oauth2client doesn't want you to set redirect_uri as part of the
        # request, which causes a lot of runtime issues.
        auth_uri = self.auth_uri
        if self.domain:
            auth_uri = auth_uri + '?hd=' + self.domain

        return OAuth2WebServerFlow(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=redirect_uri,
            user_agent='freight/{0} (python {1})'.format(
                freight.VERSION,
                PYTHON_VERSION,
            ),
            auth_uri=auth_uri,
            token_uri=self.token_uri,
            revoke_uri=self.revoke_uri
        )

    def step2_exchange(self, code, redirect_uri=None):
        resp = super(GoogleOAuth2Provider, self).step2_exchange(code,
                                                                redirect_uri)

        # Validate the domain.
        if self.domain and resp.id_token.get('hd') != self.domain:
            raise AccessDeniedError('domain %s does not match %s' %
                                    (resp.id_token.get('hd'), self.domain))

        return resp


class GitHubOAuth2Provider(OAuth2Provider):
    """GitHub OAuth 2.0 provider.
    """

    def __init__(self,
                 client_id,
                 client_secret,
                 team_id=None,
                 organization_id=None,
                 scope='user'):
        """Initialize a GitHub OAuth 2.0 provider.

        :param client_id: Client ID.
        :param client_secret: Client secret.
        :param team_id: Optional team ID to limit authorization to.
        :type team_id: :class:`int`, :class:`long`
        :param organization_id:
            Optional organization ID to limit authorization to.
        :type organization_id: :class:`int`, :class:`long`
        :param scope: Scope. Default ``user``.
        """

        self.team_id = team_id
        self.organization_id = organization_id

        super(GitHubOAuth2Provider, self).__init__(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            auth_uri=GITHUB_AUTH_URI,
            token_uri=GITHUB_TOKEN_URI
        )

    @classmethod
    def from_app_config(cls, config):
        client_id = config.get('GITHUB_CLIENT_ID')
        client_secret = config.get('GITHUB_CLIENT_SECRET')
        team_id = config.get('GITHUB_TEAM_ID')
        organization_id = config.get('GITHUB_ORGANIZATION_ID')

        if not client_id or not client_secret:
            raise ProviderConfigurationError(
                'GitHub authentication requires a client ID '
                '(GITHUB_CLIENT_ID) and secret (GITHUB_CLIENT_SECRET) to be '
                'provided'
            )

        if team_id:
            try:
                team_id = int(team_id)
            except ValueError:
                raise ProviderConfigurationError(
                    'invalid team ID (GITHUB_TEAM_ID): %s' % (team_id)
                )
        elif organization_id:
            try:
                organization_id = int(organization_id)
            except ValueError:
                raise ProviderConfigurationError(
                    'invalid organization ID (GITHUB_ORGANIZATION_ID): %s' %
                    (organization_id)
                )

            raise ProviderConfigurationError(
                'either a team ID (GITHUB_TEAM_ID) or an organization ID '
                '(GITHUB_ORGANIZATION_ID) must be configured for GitHub '
                'authentication'
            )

        return cls(client_id=client_id,
                   client_secret=client_secret,
                   team_id=team_id,
                   organization_id=organization_id)

    def _get_github_api_json(self, url, access_token):
        """Perform a GET request against the GitHub API.

        :param url: URL.
        :param access_token: Access token.
        :returns: the JSON response body on success.
        """

        resp = requests.get(url, params={'access_token': access_token})

        logger.debug('Response for %s: status code %d' % (url,
                                                          resp.status_code))

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            # GitHub will return 404 if the scope does not allow access to
            # the requested endpoint. For now, let's raise a FlowExchangeError
            # to force re-authorization, hopefully with the right scope.
            raise FlowExchangeError('insufficient_scope')

        # Any other error is hard to deal with. Let's raise it and propagate
        # the exception to, say, Sentry.
        resp.raise_for_status()

    def step1_get_authorize_url(self, redirect_uri=None):
        return self._get_flow(redirect_uri).step1_get_authorize_url()

    def step2_exchange(self, code, redirect_uri=None):
        resp = super(GitHubOAuth2Provider, self).step2_exchange(code,
                                                                redirect_uri)

        # Fetch the user's profile information.
        id_token_additions = {}

        user_json = self._get_github_api_json(GITHUB_API_USER_URI,
                                              resp.access_token)

        id_token_additions['email'] = user_json['email']
        id_token_additions['login'] = user_json['login']
        id_token_additions['id'] = user_json['id']

        # Fetch the user's teams.
        teams_json = self._get_github_api_json(GITHUB_API_USER_TEAMS_URI,
                                               resp.access_token)

        team_ids = set()
        organization_ids = set()

        for team in teams_json:
            team_ids.add(team['id'])
            organization_ids.add(team['organization']['id'])

        id_token_additions['team_ids'] = team_ids
        id_token_additions['organization_ids'] = organization_ids

        # Validate that the user should be permitted access.
        if (self.team_id and int(self.team_id) not in team_ids) or \
           (self.organization_id and
               int(self.organization_id) not in organization_ids):
            raise AccessDeniedError()

        # Update the response.
        if resp.id_token:
            resp.id_token.update(id_token_additions)
        else:
            resp.id_token = id_token_additions

        return resp
