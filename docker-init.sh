#!/bin/bash
set -e

# Check if dockerd is already running
if ! pgrep -x dockerd > /dev/null; then
    # Start dockerd in background with logging
    sudo dockerd &>/tmp/dockerd.log &
fi

# Wait for Docker to be ready
until timeout 1 docker version &>/dev/null; do sleep 1; done

# Execute the main command
exec "$@"
