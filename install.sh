#!/bin/sh
set -eu

# Install devcontainer base tools on existing Debian/Ubuntu system
# 
# Usage:
#   ./install.sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | SETUP_USER=myuser sh

echo "Installing devcontainer base for user: ${SETUP_USER:-$(whoami)}..."

# Install pipx if needed
command -v pipx >/dev/null || {
    sudo apt-get update -y
    sudo apt-get install -y pipx sudo
}

# Run build
pipx run https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py
