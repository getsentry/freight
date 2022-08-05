#!/bin/bash

set -e

# Perform an upgrade before booting up web/worker processes
case "$1" in
    web|worker)
        gosu freight upgrade
    ;;
esac

if [ -f /etc/freight/auth-helpers.sh ]; then
    . /etc/freight/auth-helpers.sh
fi

# Check if we're trying to execute a freight bin
if [ -f "/usr/src/app/bin/$1" ]; then
    set -- tini -- "$@"
    if [ "$(id -u)" = '0' ]; then
        mkdir -p "$WORKSPACE_ROOT"
        chown -R freight "$WORKSPACE_ROOT"
        set -- gosu freight "$@"
    fi
fi

exec "$@"
