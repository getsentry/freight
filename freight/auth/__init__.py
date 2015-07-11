from __future__ import absolute_import

from .exceptions import AccessDeniedError, ProviderConfigurationError  # noqa
from .providers import GoogleOAuth2Provider, GitHubOAuth2Provider


class Auth(object):
    """Flask extension for OAuth 2.0 authentication.

    Assigns the configured provider to the ``auth_provider`` key of
    ``app.state`` when initialized.
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # For compatibility with previous versions of Freight, default to using
        # Google as the authentication backend.
        backend = app.config.get('AUTH_BACKEND')
        if not backend:
            backend = 'google'

        # Resolve the provider setup function.
        try:
            provider_cls = {
                'google': GoogleOAuth2Provider,
                'github': GitHubOAuth2Provider,
            }[backend]
        except KeyError:
            raise RuntimeError('invalid authentication backend: %s' %
                               (backend))

        # Set up the provider.
        if not hasattr(app, 'state'):
            app.state = {}

        app.state['auth_provider'] = provider_cls.from_app_config(app.config)
