#!/bin/bash

set -e

if [[ "$(id -u)" != 0 ]]; then
    echo "Freight needs to be run as root user (we step down to build user before leaving the entrypoint)"
    exit 1
fi

# Perform an upgrade before booting up web/worker processes.
case "$1" in
    web|worker)
        gosu build upgrade
    ;;
esac

email=$(grep client_email /etc/freight/google-credentials.json | sed -e "s/.*: \"//" | sed -e "s/\",//")
gcloud auth activate-service-account "$email" --key-file=/etc/freight/google-credentials.json -q
unset email

# TODO: try to chown this on the host.
chown -R build:build "$WORKSPACE_ROOT"

exec tini gosu build "$@"
