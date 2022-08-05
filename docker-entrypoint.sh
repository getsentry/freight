#!/bin/bash

set -e

# Unfortunately we can't remove gosu, we need to start the container
# as root to at least chown WORKSPACE_ROOT since on garbage, that is
# owned by td-agent:root.
# TODO(newfreight): everything that Freight volume mounts should
# be owned by build user (uid 9010). Then we can remove gosu,
# and straight up run as build.

# Perform an upgrade before booting up web/worker processes.
case "$1" in
    web|worker)
        gosu build upgrade
    ;;
esac

if [ -f /etc/freight/auth-helpers.sh ]; then
    . /etc/freight/auth-helpers.sh
fi

# Check if we're trying to execute a freight bin as root.
# If so, we'll want to drop to running it as the build user (uid 9010).
if [ -f "/usr/src/app/bin/$1" ]; then
    set -- tini -- "$@"
    if [ "$(id -u)" = '0' ]; then
        mkdir -p "$WORKSPACE_ROOT"
        chown -R build "$WORKSPACE_ROOT"
        set -- gosu build "$@"
    fi
fi

exec "$@"
