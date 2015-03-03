Freight
-------

**This project is a work in progress and is not yet intended to be production ready.**

This service is intended to augment your existing deployment processes. It should improve on what you may already have, or help you fill in what you're missing.

The overarching goal of the system is to provide easy manual and automated deploys, with a consistent central view of the world. It's heavily inspired by GitHub's processes (and its Heaven project) as well as personal experiences of internal tools from members of the Sentry team.

It's not designed to replace something like Heroku, or other PaaS services, but rather to work *with* your existing processes, no matter what they are.

.. image:: https://www.herokucdn.com/deploy/button.png
  :alt: Deploy
  :target: https://heroku.com/deploy

Current Features
================

- Works behind-firewall (no inbound traffic)
- Multiple applications. All configuration is unique per application
- Per-environment deployments (i.e. different versions on staging and production)
- Workspace management (i.e. whatever your deploy command is may be generating local artifacts, those should be cleaned up)
- Support for at least Fabric-based (simple shell commands) and Heroku-based deploys
- API-accessible deploy logs
- Hubot integration (starting deploys)
- Slack integraiton (notifying when deploys start/finish/fail)
- Integration with GitHub status checks (i.e. did Circle CI pass on sha XXX)

Roadmap
=======

V0
~~

- Release state management (know what versions are active where, and provide a historical view)
- Environment locking (i.e. prevent people from deploying to an environment)
- Automatic deploys (i.e. by looking for VCS changes)
- A GUI to manage deploys as well as view logs

V1
~~

- Deploy queue (i.e. cramer queued sha XXX, armin queued sha YYY)

V2 and Beyond
~~~~~~~~~~~~~

**Machine-consistency service**

We could run a service on each machine that would check-in with the master. This would record the current version of the application. The service would be configured with a set of apps (their environment info, how to get app version). The service could also be aware of "how do I deploy a version" which could assist in pull-based deploys.

Setup
=====

In order to get Freight running you'll need a couple things:

- A `Google Developer <https://console.developers.google.com/>`_ account in order to create an OAuth2 `webserver application <https://developers.google.com/accounts/docs/OAuth2WebServer>`_.
- A `Sentry` <http://getsentry.com>`_ account.

Configuration
~~~~~~~~~~~~~

Configuration can be managed either via a Python file, or selectively via environment variables. Generally there are sane defaults available where appropriate, though many things are install-specific.

If you're using a configuration file you'll need to pass it with `FREIGHT_CONF` environment variable:

.. code-block: bash

  FREIGHT_CONF=/tmp/freight.conf.py bin/web

The following values should be configured:

GOOGLE_CLIENT_ID
  The client ID for the Google application.

GOOGLE_CLIENT_SECRET
  The client ID for the Google application.

GOOGLE_DOMAIN
  The Google Apps domain to restrict authentication to.

SENTRY_DSN
  A DSN value from Sentry.

SSH_PRIVATE_KEY
  The SSH private key required for cloning repositories (newlines replaced with \n). This will also be made available to providers as a file-system resource.

DEFAULT_TIMEOUT
  The default timeout for deploys.


GitHub
~~~~~~

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


An Example Fabric Configuration
===============================

Our example will use the `Curlish <http://pythonhosted.org/curlish/>`_ utility and the local server with its default key:

.. code-block: bash

  curlish http://localhost:5000/api/0/apps/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70' \
      -X POST \
      -J repository=git@github.com:my-organization/example.git \
      -J name=example \
      -J provider=shell \
      -J provider_config='{"command": "bin/fab -a -i {ssh_key} -R {environment} {task}:sha={sha}"}'

The important part here is our provider configuration:

.. code-block: json

  {
      "command": "bin/fab -a -i {ssh_key} -R {environment} {task}:sha={sha}"
  }


The command we're passing is simply a wrapper around Fabric:

.. code-block: bash

  #!/bin/bash

  # Usage: bin/fab [arguments]
  # Wrapper around Fabric which ensures any required dependencies are installed.

  pip install fabric pytz
  fab $@


.. note:: This file is not part of Freight, but rather it's referencing a path relative to your repository root.

Now we can create a new deploy task:

.. code-block: bash

  curlish http://localhost:5000/api/0/tasks/ \
      -H 'Authorization: Key 3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70'
      -X POST \
      -J app=example \
      -J ref=master \
      -J task=deploy \
      -J user="user@example.com"

In our response we'll get back the task summary which simply notes its pending and gives you it's ID:

.. code-block: json

  {
    "id": "1",
    "status": "pending"
  }

In the future you will be able to poll the logs via the API, as well as the task status.

See Also
========

- `freight-cli <https://github.com/getsentry/freight-cli>`_
- `hubot-freight <https://github.com/getsentry/hubot-freight>`_
