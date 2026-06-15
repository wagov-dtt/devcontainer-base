#!/bin/sh
set -eu

# Install wagov devcontainer tools on an existing system via mise bootstrap.
#
# Usage:
#   ./install.sh
#   curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
#   SETUP_USER=myuser curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
#   SETUP_USER=myuser ./install.sh

DEVCONTAINER_BASE_REF="${DEVCONTAINER_BASE_REF:-main}"
DEVCONTAINER_BASE_URL="${DEVCONTAINER_BASE_URL:-https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/${DEVCONTAINER_BASE_REF}}"

echo "Installing wagov devcontainer via mise bootstrap..."

as_root() {
  if [ "$(id -u)" = "0" ]; then
    "$@"
  else
    sudo "$@"
  fi
}

# Detect platform
if [ -d /run/ostree-booted ] 2>/dev/null || grep -qE '^(ID|VARIANT_ID|IMAGE_ID)=(aurora|bazzite|bluefin|bootc|kinoite|sericea|silverblue)' /etc/os-release 2>/dev/null; then
  PLATFORM=brew
elif [ -x /usr/bin/apt-get ] && (grep -qE '^ID=(debian|ubuntu)' /etc/os-release 2>/dev/null || true); then
  PLATFORM=apt
elif command -v brew >/dev/null 2>&1; then
  PLATFORM=brew
else
  PLATFORM=apt
fi

if [ "$PLATFORM" = apt ]; then
  # APT pre-bootstrap: install extrepo/curl and enable repos before mise is needed.
  echo "Preparing APT repositories..."
  as_root apt-get update -y
  as_root apt-get install -y extrepo curl gnupg locales sudo
  as_root locale-gen en_US.UTF-8
  as_root sed -i 's/^# - contrib/- contrib/' /etc/extrepo/config.yaml
  as_root sed -i 's/^# - non-free/- non-free/' /etc/extrepo/config.yaml
  for repo in docker-ce github-cli kubernetes google_cloud ddev mise hashicorp; do
    as_root extrepo enable "$repo" || echo "extrepo: $repo skipped or already enabled"
  done
elif [ "$PLATFORM" = brew ]; then
  echo "Detected brew-based host..."
fi

# Install mise if missing
if ! command -v mise >/dev/null 2>&1; then
  echo "Installing mise..."
  if [ "$(id -u)" = "0" ]; then
    curl --proto '=https' --tlsv1.2 -sSf https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
  else
    mkdir -p "$HOME/.local/bin"
    curl --proto '=https' --tlsv1.2 -sSf https://mise.run | MISE_INSTALL_PATH="$HOME/.local/bin/mise" sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

if [ -z "${GITHUB_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
  export GITHUB_TOKEN
fi

# Fetch config from repo
tmpdir="$(mktemp -d)"
chmod 755 "$tmpdir"
trap 'rm -rf "$tmpdir"' EXIT

fetch_config() {
  if command -v curl >/dev/null 2>&1; then
    curl -sSL "${DEVCONTAINER_BASE_URL}/$1" -o "$2"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "${DEVCONTAINER_BASE_URL}/$1" -O "$2"
  else
    echo "ERROR: Neither curl nor wget found. Install one of them first." >&2
    exit 1
  fi
}

fetch_config mise.toml "$tmpdir/mise.toml"

if [ "$PLATFORM" = apt ]; then
  fetch_config mise.apt.toml "$tmpdir/mise.apt.toml"
elif [ "$PLATFORM" = brew ]; then
  fetch_config mise.brew.toml "$tmpdir/mise.brew.toml"
fi

# Trust and bootstrap
cd "$tmpdir"
mise trust --yes .

if [ -n "${SETUP_USER:-}" ]; then
  if [ "$(id -u)" = "0" ]; then
    if [ "$PLATFORM" = apt ]; then
      # APT packages are system-level; install them as root, then configure the target user.
      mise bootstrap packages install --yes --update -E apt
      sudo -Hu "$SETUP_USER" mise trust --yes "$tmpdir"
      sudo -Hu "$SETUP_USER" mise bootstrap --yes
    else
      # Homebrew is user-space on supported hosts; run the full brew bootstrap as the target user.
      sudo -Hu "$SETUP_USER" mise trust --yes "$tmpdir"
      sudo -Hu "$SETUP_USER" mise bootstrap --yes -E brew
    fi
  else
    if [ "$SETUP_USER" != "$(id -un)" ]; then
      echo "ERROR: SETUP_USER requires running as root; current user is $(id -un), requested $SETUP_USER" >&2
      exit 1
    fi
    echo "Configuring as user: $SETUP_USER"
    mise bootstrap --yes -E "$PLATFORM"
  fi
else
  mise bootstrap --yes -E "$PLATFORM"
fi

echo "Wagov devcontainer bootstrap complete!"
