#!/bin/sh
set -eu

# Install wagov devcontainer tools on an existing system.
#
# Usage:
#   ./install.sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh -s -- --user myuser
#   SETUP_USER=myuser ./install.sh

export SETUP_USER="${SETUP_USER:-$(whoami)}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo "")}" 

echo "Installing wagov devcontainer for user: ${SETUP_USER}..."

if command -v uvx >/dev/null 2>&1; then
    exec uvx wagov-devcontainer "$@"
fi

if command -v pipx >/dev/null 2>&1; then
    exec pipx run --spec wagov-devcontainer wagov-devcontainer "$@"
fi

if command -v apt-get >/dev/null 2>&1; then
    if [ "$(id -u)" = "0" ]; then
        apt-get update -y && apt-get install -y pipx sudo
    else
        sudo apt-get update -y && sudo apt-get install -y pipx sudo
    fi

    exec pipx run --spec wagov-devcontainer wagov-devcontainer "$@"
fi

cat >&2 <<'EOF'
No supported bootstrap method found.

Install one of these first, then rerun:
  - uv (for `uvx wagov-devcontainer`)
  - pipx (for `pipx run --spec wagov-devcontainer wagov-devcontainer`)

The helper script only bootstraps pipx automatically on APT-based systems.
On atomic hosts such as Bluefin, use uvx or pipx directly.
EOF
exit 1
