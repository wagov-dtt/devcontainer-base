#!/bin/sh
set -eu

# Install devcontainer base tools on existing Debian/Ubuntu system
# 
# Usage:
#   ./install.sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | SETUP_USER=myuser sh

export SETUP_USER="${SETUP_USER:-$(whoami)}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo "")}"
echo "Installing devcontainer base for user: ${SETUP_USER}..."

# Install pipx if needed
command -v pipx >/dev/null || {
    if [ "$(id -u)" = "0" ]; then
        apt-get update -y && apt-get install -y pipx sudo
    else
        sudo apt-get update -y && sudo apt-get install -y pipx sudo
    fi
}

# Run build
pipx run https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py
