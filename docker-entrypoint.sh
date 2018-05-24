#!/bin/bash

set -e

# Perform an upgrade before booting up web/worker processes
case "$1" in
    web|worker)
        gosu freight upgrade
    ;;
esac

if [ "$DOCKER_CONFIG" ]; then
    gosu freight bash -c 'mkdir -p ~/.docker'
    gosu freight bash -c 'echo $DOCKER_CONFIG > ~/.docker/config.json'
    gosu freight bash -c 'chmod 400 ~/.docker/config.json'
    # Make sure we don't pass this along since it contains sensitive info
    unset DOCKER_CONFIG
fi

if [ "$GCP_PROJECT" ]; then
    gosu freight bash -c 'mkdir -p ~/.config/gcloud/configurations/'
    gosu freight bash -c "cat <<- 'HERE' > ~/.config/gcloud/configurations/config_default
	[core]
	project = $GCP_PROJECT

	[compute]
	zone = $GCP_ZONE
	region = $GCP_REGION
HERE"
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
