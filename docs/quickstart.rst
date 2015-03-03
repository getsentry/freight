Quickstart
==========

The easiest way to get started is to run Freight on Heroku:

.. image:: https://www.herokucdn.com/deploy/button.png
  :alt: Deploy
  :target: https://heroku.com/deploy


Otherwise, you'll need the following services available:

- Redis (or any `Celery <http://http://www.celeryproject.org/>`_) compatible broker)
- PostgreSQL

.. note:: Freight is designed to support behind-firewall installation. However, this guide does not yet cover all required configuration.


Configuration
-------------

Configuration can be managed either via a Python file, or selectively via environment variables. Generally there are sane defaults available where appropriate, though many things are install-specific.

If you're using a configuration file you'll need to pass it with ``FREIGHT_CONF`` environment variable:

.. code-block:: bash

  FREIGHT_CONF=/tmp/freight.conf.py bin/web

The following values should be configured:

SSH_PRIVATE_KEY
  The SSH private key required for cloning repositories (newlines replaced with \n). This will also be made available to providers as a file-system resource.

DEFAULT_TIMEOUT
  The default timeout for deploys.

Google Authentication
~~~~~~~~~~~~~~~~~~~~~

The frontend currently only supports authenticating with Google. You'll need a `Google Developer <https://console.developers.google.com/>`_ account in order to create an OAuth2 `webserver application <https://developers.google.com/accounts/docs/OAuth2WebServer>`_.

GOOGLE_CLIENT_ID
  The client ID for the Google application.

GOOGLE_CLIENT_SECRET
  The client ID for the Google application.

GOOGLE_DOMAIN
  The Google Apps domain to restrict authentication to.


GitHub Checks
~~~~~~~~~~~~~

To integrate GitHub context checks you'll need to generate an API token:

.. code-block:: bash

  curlish https://api.github.com/authorizations \
      -u your-username \
      -X POST \
      -J scopes='repo' \
      -J note='freight'

The following configuration is available:

GITHUB_TOKEN
  The generated API token.
GITHUB_API_ROOT
  The base URL for the API. Defaults to ``https://api.github.com``


Sentry Reporting
~~~~~~~~~~~~~~~~

Support exists for reporting internal errors to an upstream `Sentry <https://getsentry.com>`_ server.

SENTRY_DSN
  A DSN value from Sentry.


An Example Fabric Configuration
-------------------------------

Our example will use the `Curlish <http://pythonhosted.org/curlish/>`_ utility and the local server with its default key:

.. code-block:: bash

  curlish http://localhost:5000/api/0/apps/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70' \
      -X POST \
      -J repository=git@github.com:my-organization/example.git \
      -J name=example \
      -J provider=shell \
      -J provider_config='{"command": "bin/fab -a -i {ssh_key} -R {environment} {task}:sha={sha}"}'

The important part here is our provider configuration:

.. code-block:: json

  {
      "command": "bin/fab -a -i {ssh_key} -R {environment} {task}:sha={sha}"
  }


The command we're passing is simply a wrapper around Fabric:

.. code-block:: bash

  #!/bin/bash

  # Usage: bin/fab [arguments]
  # Wrapper around Fabric which ensures any required dependencies are installed.

  pip install fabric pytz
  fab $@


.. note:: This file is not part of Freight, but rather it's referencing a path relative to your repository root.

Now we can create a new deploy task:

.. code-block:: bash

  curlish http://localhost:5000/api/0/tasks/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70'
      -X POST \
      -J app=example \
      -J ref=master \
      -J task=deploy \
      -J user="user@example.com"

In our response we'll get back the task summary which simply notes its pending and gives you it's ID:

.. code-block:: json

  {
    "id": "1",
    "status": "pending"
  }

You can now query the API for the given task, or simply load up the web UI.
