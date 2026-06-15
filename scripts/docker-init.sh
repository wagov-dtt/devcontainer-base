#!/bin/sh
set -eu

docker_host="${DOCKER_HOST:-}"

if [ -z "$docker_host" ]; then
    sock="/var/run/docker.sock"
elif [ "${docker_host#unix://}" != "$docker_host" ]; then
    sock="${docker_host#unix://}"
else
    echo "DOCKER_HOST is not a Unix socket: $docker_host"
    exit 0
fi

if [ ! -S "$sock" ]; then
    echo "No Docker socket found at $sock"
    exit 0
fi

socket_gid="$(stat -c '%g' "$sock")"
docker_gid="$(getent group docker | cut -d: -f3 || true)"

if [ "$docker_gid" = "$socket_gid" ]; then
    exit 0
fi

if sudo groupmod -g "$socket_gid" docker; then
    echo "Updated Docker GID to $socket_gid"
else
    echo "Docker GID update skipped"
fi
