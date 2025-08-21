#!/bin/bash
set -euo pipefail

echo "Installing devcontainer base for user: ${SETUP_USER:-$(whoami)}..."

# Install pipx if needed
command -v pipx >/dev/null || {
    sudo apt-get update -y
    sudo apt-get install -y pipx sudo
}

# Run build
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py | \
    pipx run pyinfra @local -y /dev/stdin
