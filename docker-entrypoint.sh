#!/bin/bash

set -e

# Perform an upgrade before booting up web/worker processes
case "$1" in
    web|worker)
        upgrade
    ;;
esac

exec "$@"
