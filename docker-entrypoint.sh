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

export GOOGLE_APPLICATION_CREDENTIALS=/home/freight/google-credentials.json

# copy the file to someplace we can set permissions
# REMINDER: this file MUST persist or periodic auth refresh WILL FAIL and revert to any auth it can find
#    (e.g. garbage's instance credentials)
cp /etc/freight/google-credentials.json ${GOOGLE_APPLICATION_CREDENTIALS}
chown freight ${GOOGLE_APPLICATION_CREDENTIALS}

email=$(cat ${GOOGLE_APPLICATION_CREDENTIALS} | grep client_email | sed -e "s/.*: \"//" | sed -e "s/\",//")

gosu freight bash -c "gcloud auth activate-service-account ${email} --key-file=${GOOGLE_APPLICATION_CREDENTIALS} -q" # this sets up region/zone based on key file

unset email

mkdir -p /home/freight/.docker/
chown freight:freight /home/freight/.docker/
cp /etc/freight/config.json /home/freight/.docker/config.json
chown freight:freight /home/freight/.docker/config.json

exec tini "$@"
