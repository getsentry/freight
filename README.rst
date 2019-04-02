Freight
-------

**This project is a work in progress and is not yet intended to be
production ready.**

This service is intended to augment your existing deployment processes. It
should improve on what you may already have, or help you fill in what
you're missing.

The overarching goal of the system is to provide easy manual and automated
deploys, with a consistent central view of the world. It's heavily
inspired by GitHub's processes (and its Heaven project) as well as
personal experiences of internal tools from members of the Sentry team.

It's not designed to replace something like Heroku, or other PaaS
services, but rather to work *with* your existing processes, no matter
what they are.

Current Features
================

- Works behind-firewall (no inbound traffic)
- Multiple applications. All configuration is unique per application
- Per-environment deployments (i.e. different versions on staging and production)
- Workspace management (i.e. whatever your deploy command is may be generating local artifacts, those should be cleaned up)
- Support for at least Fabric-based (simple shell commands) and Heroku-based deploys
- API-accessible deploy logs
- Hubot integration (starting deploys)
- Slack integration (notifying when deploys start/finish/fail)
- Sentry integration (release tracking, error reporting)
- Integration with GitHub status checks (i.e. did Circle CI pass on sha XXX)
- A GUI to get an overview of deploy status and history

Roadmap
=======

What's coming up:

V0
~~

- Release state management (know what versions are active where, and provide a historical view)
- Environment locking (i.e. prevent people from deploying to an environment)
- Automatic deploys (i.e. by looking for VCS changes)
- Actions within the GUI (deploy, cancel)

V1
~~

- Deploy queue (i.e. cramer queued sha XXX, armin queued sha YYY)

V2 and Beyond
~~~~~~~~~~~~~

**Machine-consistency service**

We could run a service on each machine that would check-in with the
master. This would record the current version of the application. The
service would be configured with a set of apps (their environment info,
how to get app version). The service could also be aware of "how do I
deploy a version" which could assist in pull-based deploys.


Resources
=========

- `Documentation <https://freight.readthedocs.io>`_
- `Bug Tracker <https://github.com/getsentry/freight/issues>`_
- `Code <https://github.com/getsentry/freight>`_
- `IRC <irc://irc.freenode.net/sentry>`_  (irc.freenode.net, #sentry)
