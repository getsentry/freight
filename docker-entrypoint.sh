#!/bin/bash

set -e

# Perform an upgrade before booting up web/worker processes.
case "$1" in
    web|worker)
        gosu build upgrade
    ;;
esac

email=$(grep client_email /etc/freight/google-credentials.json | sed -e "s/.*: \"//" | sed -e "s/\",//")
gcloud auth activate-service-account "$email" --key-file=/etc/freight/google-credentials.json -q
unset email

mkdir -p /home/build/.docker/
chown build:build /home/build/.docker/
cp /etc/freight/config.json /home/build/.docker/config.json
chown build:build /home/build/.docker/config.json

chown -R build:build "$WORKSPACE_ROOT"

exec tini gosu build "$@"
