#!/bin/bash

set -e

# Perform an upgrade before booting up web/worker processes
case "$1" in
    web|worker)
        gosu freight upgrade
    ;;
esac

# set up GCP service account auth
# this file must be chowned to freight and mounted to this location
export GOOGLE_APPLICATION_CREDENTIALS=/home/freight/google-credentials.json
email=$(grep 'client_email' "$GOOGLE_APPLICATION_CREDENTIALS" | sed -e "s/.*: \"//" | sed -e "s/\",//")
gosu freight bash -c "gcloud auth activate-service-account ${email} --key-file=${GOOGLE_APPLICATION_CREDENTIALS} -q"
unset email

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
