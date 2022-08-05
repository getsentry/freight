#!/bin/bash

set -e

if [[ "$(id -u)" != 9010 ]] || [[ "$(id -un)" != build ]]; then
    echo "Freight needs to be run as user build with uid 9010."
    exit 1
fi

# Perform an upgrade before booting up web/worker processes.
case "$1" in
    web|worker)
        upgrade
    ;;
esac

if [ -f /etc/freight/auth-helpers.sh ]; then
    . /etc/freight/auth-helpers.sh
fi

exec tini "$@"
