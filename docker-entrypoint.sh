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

email=$(grep client_email /etc/freight/google-credentials.json | sed -e "s/.*: \"//" | sed -e "s/\",//")
gcloud auth activate-service-account "$email" --key-file=/etc/freight/google-credentials.json -q
unset email

mkdir -p /home/build/.docker/
chown build:build /home/build/.docker/
cp /etc/freight/config.json /home/build/.docker/config.json
chown build:build /home/build/.docker/config.json

exec tini "$@"
