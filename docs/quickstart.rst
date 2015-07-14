Quickstart
==========

The easiest way to get started is to run Freight on Heroku:

.. image:: https://www.herokucdn.com/deploy/button.png
  :alt: Deploy
  :target: https://heroku.com/deploy

Requirements
------------

.. note:: Freight is designed to support behind-firewall installation. However, this guide does not yet cover all required configuration.

If you're not using Heroku, you'll need to ensure a few server dependencies:

- Redis (or any `Celery <http://www.celeryproject.org/>`_ compatible broker)
- PostgreSQL
- Python 2.7
- Node.js

Dependencies
------------

Freight contains dependencies both from Python (for the API and workers) and JavaScript (for the frontend). We recommend using a virtualenv, but we're not going to cover that in our quickstart guide.

Start by installing Python dependencies:

.. code-block:: bash

  python setup.py develop

And then install the JavaScript dependencies:

.. code-block:: bash

  npm install


Configuration
-------------

Configuration can be managed either via a Python file, or selectively via environment variables. Generally there are sane defaults available where appropriate, though many things are install-specific.

If you're using a configuration file you'll need to pass it with ``FREIGHT_CONF`` environment variable:

.. code-block:: bash

  FREIGHT_CONF=/tmp/freight.conf.py bin/web

The following values should be configured:

.. option:: API_KEY

  The API key clients will use to communicate with Freight.

.. option:: SSH_PRIVATE_KEY

  The SSH private key required for cloning repositories (newlines replaced with ``\n``). This will also be made available to providers as a file-system resource.

.. option:: DEFAULT_TIMEOUT

  The default timeout for deploys.

Google Authentication
~~~~~~~~~~~~~~~~~~~~~

The frontend currently only supports authenticating with Google. You'll need a `Google Developer <https://console.developers.google.com/>`_ account in order to create an OAuth2 `webserver application <https://developers.google.com/accounts/docs/OAuth2WebServer>`_.
Set its *Redirect URI* to `$HOST/auth/complete/`.

.. option:: GOOGLE_CLIENT_ID

  The client ID for the Google application.

.. option:: GOOGLE_CLIENT_SECRET

  The client ID for the Google application.

.. option:: GOOGLE_DOMAIN

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

.. option:: GITHUB_TOKEN

  The generated API token.

.. option:: GITHUB_API_ROOT

  The base URL for the API. Defaults to ``https://api.github.com``


Sentry Reporting
~~~~~~~~~~~~~~~~

Support exists for reporting internal errors to an upstream `Sentry <https://getsentry.com>`_ server.

.. option:: SENTRY_DSN

  A DSN value from Sentry.


Bootstrap the Database
----------------------

.. note:: If you're on Heroku, you can skip this step.

If you haven't already, create a new database for Freight:

.. code-block:: bash

  createdb -E utf-8 freight

Now apply Freight's migrations:


.. code-block:: bash

  bin/upgrade


Webserver
---------

At this point you should have a working installation. To test this, launch the webserver:

.. code-block:: bash

  bin/web

You should then be able to access the frontend: http://localhost:5000


Creating an Application
-----------------------

.. note:: Our examples will use the `Curlish <http://pythonhosted.org/curlish/>`_ utility and the local server with its default key.

With the webserver online, you should be able to access the API. The first thing you'll need to do is create an application:

.. code-block:: bash

  curlish http://localhost:5000/api/0/apps/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70' \
      -X POST \
      -J repository=git@github.com:my-organization/example.git \
      -J name=example \
      -J provider=shell \
      -J provider_config='{"command": "bin/fab -a -i {ssh_key} -R {environment} {task}:sha={sha}"}'

We've created a new application named "example" using the shell provider.

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

.. note:: This bin/fab file is not part of Freight, but rather it's referencing a path relative to your repository root.


Creating a new Deploy
---------------------

Once we've configured our application we can create a new deploy:

.. code-block:: bash

  curlish http://localhost:5000/api/0/tasks/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70' \
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


Monitoring a Deploy
-------------------

While Freight intends to provide a feature-rich frontend, it's fundamentally an API-driven application.

For example, to get the status of a deploy:


.. code-block:: bash

  curlish http://localhost:5000/api/0/tasks/1/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70'

Additionally you can access the logs via the API:

.. code-block:: bash

    curlish http://localhost:5000/api/0/tasks/1/log/?offset=-1&limit=1000 \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70'


Rolling Back
------------

While Freight doesn't formally offer a first-class rollback control, you can tell it to deploy the previous stable:

.. code-block:: bash

  curlish http://localhost:5000/api/0/tasks/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70' \
      -X POST \
      -J app=example \
      -J ref=:previous \
      -J task=deploy \
      -J user="user@example.com"


Next Steps
----------

We've gone through the basics of creating an application and firing off a deploy. Two important pieces that aren't yet covered in the quickstart include pre-deploy checks and notifications. To learn more about those, we recommend diving into the code.

