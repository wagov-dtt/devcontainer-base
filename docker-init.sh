#!/bin/bash
set -e

# Start dockerd in background with logging
sudo dockerd &>/tmp/dockerd.log &

# Wait for Docker to be ready
until timeout 1 docker version &>/dev/null; do sleep 1; done

# Execute the main command
exec "$@"
