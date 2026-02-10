#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyinfra>=3",
# ]
# ///
"""
Devcontainer build using pyinfra @local connector.
Run with `pipx` or `uv`:
- pipx run <url>/build.py
- uv run <url>/build.py
- pipx run build.py
- pipx run pyinfra @local -y build.py

Environment variables:
- SETUP_USER: User to configure (default: current user)
"""

if __name__ == "__main__":
    import sys
    import tempfile

    from pyinfra_cli.main import cli

    with tempfile.NamedTemporaryFile(delete_on_close=False, mode="w", suffix=".py") as tmpfile:
        # If being directly executed, save file to a deploy file pyinfra can use
        if sys.orig_argv[1] == "-c":
            tmpfile.write(sys.orig_argv[2])
            tmpfile.close()
            build_py = tmpfile.name
        else:
            build_py = sys.orig_argv[1]

        # Set sys.argv to simulate command line arguments
        sys.argv = ["pyinfra", "@local", "-y", build_py]

        # Call cli function directly
        cli()

import getpass
import io
import os
import pathlib

from pyinfra import config, host
from pyinfra.facts.files import FileContents
from pyinfra.facts.server import LinuxDistribution
from pyinfra.operations import apt, files, python, server, systemd

# APT repositories (extrepo)
APT_REPOS = [
    "docker-ce",
    "github-cli",
    "kubernetes",
    "google_cloud",
    "ddev",
    "mise",
    "hashicorp",
]

# APT packages configuration
APT_PACKAGES = (
    # Container & Development
    [
        "extrepo",
        "docker-ce-cli",
        "docker-buildx-plugin",
        "docker-compose-plugin",
        "git",
        "neovim",
        "build-essential",
        "python3-dev",
    ]
    # Cloud & Infrastructure
    + [
        "mise",
        "gh",
        "terraform",
        "ddev",
        "kubectl",
        "kustomize",
    ]
    # System & Utilities
    + [
        "sudo",
        "tini",
        "openssh-client",
        "bash-completion",
        "locales",
        "ripgrep",
        "ugrep",
        "jq",
        "less",
        "unzip",
        "zip",
        "file",
        "rsync",
        "librsvg2-bin",
    ]
    # Monitoring & Network Tools
    + [
        "btop",
        "htop",
        "procps",
        "lsof",
        "iputils-ping",
        "dnsutils",
        "net-tools",
        "restic",
        "rclone",
        "wget",
        "fzf",
    ]
)

# Mise tools configuration
# Simple: "tool-name" -> becomes "tool-name" = "latest" in TOML
# Complex: ("tool-name", '{ TOML inline table }') -> becomes "tool-name" = { ... } in TOML
MISE_TOOLS = (
    # Languages & Package Management
    [
        "go",
        "node",
        "python",
        "pnpm",
        "uv",
        "pipx",
        "cargo-binstall",
        "github:railwayapp/railpack",
    ]
    # Cloud & Infrastructure
    + [
        "aws-cli",
        "aws-sam",
        "localstack",
        "helm",
        "k9s",
        "k3d",
        "tflint",
        "terraform-docs",
        "vault",
    ]
    # Security & Quality
    + ["trivy", "cosign", "slsa-verifier", "semgrep", "lychee"]
    # Shell & Development Tools
    + [
        "just",
        "yq",
        "zellij",
        "starship",
        "zoxide",
        "eza",
        "direnv",
        "lazygit",
        "hurl",
        "envsubst",
    ]
    # AI & Development Tools
    + [
        "github:block/goose",
        (
            "pipx:litellm",
            '{ version = "latest", extras = "proxy", uvx_args = "--with boto3" }',
        ),
        "opencode",
    ]
    # Documentation & Utilities
    + [
        "pipx:tldr",
        "pipx:httpie",
        "cargo:mdbook",
        "npm:@devcontainers/cli",
        "rumdl",
        "github:boyter/scc",
    ]
)


def format_mise_tool(tool):
    if isinstance(tool, str):
        return f'"{tool}" = "latest"'
    elif isinstance(tool, tuple):
        name, config = tool
        return f'"{name}" = {config}'
    raise ValueError(f"Unexpected tool type: {type(tool)}")


MISE_TOML = f"""
[settings]
lockfile = true
pipx.uvx = true
python.compile = false
trusted_config_paths = ["/workspaces"]

[tools]
{"\n".join([format_mise_tool(tool) for tool in MISE_TOOLS])}
"""

BASHRC = io.StringIO(
    "\n".join(host.get_fact(FileContents, "/etc/skel/.bashrc"))
    + """
# Shell enhancements
eval "$(mise activate bash)"
eval "$(starship init bash)"
eval "$(zoxide init bash)"
"""
)

config.SUDO = True

# Check Debian version and warn if not Trixie
distro = host.get_fact(LinuxDistribution)
if distro and distro.get("name") == "Debian":
    version = distro.get("major", "")
    codename = distro.get("release_meta", {}).get("CODENAME", "")
    if codename != "trixie" and version != "13":
        print(f"Warning: This devcontainer is designed for Debian 13 (Trixie), but detected {distro.get('name')} {version} ({codename})")
        print("Consider upgrading to Debian Trixie for optimal compatibility")

# Get setup user from environment or current user
user = os.getenv("SETUP_USER", getpass.getuser())
server.user(user=user, create_home=True)

# Configure sudo and locale
files.block(content=f"{user} ALL=(ALL) NOPASSWD:ALL", path=f"/etc/sudoers.d/{user}")
files.file(path=f"/etc/sudoers.d/{user}", mode=440)
apt.packages(packages=["curl", "gnupg", "locales", "extrepo"], update=True)
server.locale("en_US.UTF-8")

# Configure extrepo to enable non-free policies
files.line(
    name="Enable contrib policy",
    path="/etc/extrepo/config.yaml",
    line="# - contrib",
    replace="- contrib",
)
files.line(
    name="Enable non-free policy",
    path="/etc/extrepo/config.yaml",
    line="# - non-free",
    replace="- non-free",
)

# Setup repositories (extrepo)
for repo in APT_REPOS:
    server.shell(commands=f"extrepo enable {repo}")
apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True)

# Install Docker daemon only on bare metal (systemd present, not in container builds)
if pathlib.Path("/run/systemd/system").is_dir():
    apt.packages(name="Install Docker daemon (bare metal)", packages=["docker-ce", "containerd.io"])

# Ensure docker group exists (docker-ce-cli doesn't create it, only docker-ce does)
server.shell(name="Ensure docker group", commands="groupadd -f docker")

# Docker socket init script (fixes permissions and API version at container start)
DOCKER_INIT = io.StringIO("""\
#!/bin/bash
SOCK="/var/run/docker.sock"

# 1. Guard clause: Exit cleanly if socket missing
if [ ! -S "$SOCK" ]; then
    echo "No Docker socket found at $SOCK"
    exit 0
fi

# 2. Fix Permissions
# Logic: Try to modify. If it works, log it. If it fails (already set), log alternate message.
GID=$(stat -c '%g' "$SOCK")
sudo groupmod -g "$GID" docker 2>/dev/null \
    && echo "Updated Docker GID to $GID" \
    || echo "Docker GID check: Skipped (Already set or permission denied)"

# 3. API Version
# Logic: Fetch with 2s timeout. If valid, write to file and log.
VER=$(curl -sf -m 2 --unix-socket "$SOCK" http://localhost/version | jq -r .ApiVersion 2>/dev/null)

if [ -n "$VER" ] && [ "$VER" != "null" ]; then
    echo "DOCKER_API_VERSION=$VER" | sudo tee -a /etc/environment > /dev/null
    echo "Set DOCKER_API_VERSION=$VER"
else
    echo "Warning: Could not detect Docker API version"
fi

# 4. Always exit success to prevent container build failure
exit 0
""")
files.put(name="Docker init script", src=DOCKER_INIT, dest="/usr/local/bin/docker-init.sh")
files.file(path="/usr/local/bin/docker-init.sh", mode="755")

# Configure user groups and Docker service (for bare metal installs with systemd)
server.user(name="Configure groups", user=user, shell="/bin/bash", groups=["sudo", "docker"])
systemd.service(service="docker", enabled=False, user_mode=True, _su_user=user, _ignore_errors=True)
systemd.service(service="docker", enabled=True, running=True, _ignore_errors=True)


# Configure home dir
def in_home(state, host):
    _status, _stdout = host.run_shell_command(f"getent passwd {user} | cut -d: -f6")
    home = _stdout.output.strip()

    # Mise config/install
    files.directory(path=f"{home}/.config/mise", user=user, group=user, mode="755")
    files.block(
        name="Mise config",
        path=f"{home}/.config/mise/config.toml",
        try_prevent_shell_expansion=True,
        content=MISE_TOML,
    )
    files.file(path=f"{home}/.config/mise/config.toml", user=user, group=user, mode="644")
    server.shell(
        commands="mise install --yes",
        _env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
        _sudo=True,
        _su_user=user,
    )

    # Shell configuration
    files.put(name="Shell extras", src=BASHRC, dest=f"{home}/.bashrc", _sudo_user=user)
    # Fix home directory ownership recursively
    server.shell(commands=f"find {home} -maxdepth 2 -type d -exec chown {user}:{user} {{}} \\;")


python.call(function=in_home)
