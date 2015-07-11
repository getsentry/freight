from __future__ import absolute_import


class AccessDeniedError(Exception):
    """Access denied.

    Raised if authentication with the backend succeeded but the user is not
    allowed access by configuration.
    """

    pass


class ProviderConfigurationError(Exception):
    """Provider configuration error.
    """

    pass
