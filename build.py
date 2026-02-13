#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyinfra>=3",
#   "tenacity>=8",
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
    import argparse
    import os
    import sys
    import tempfile

    from pyinfra_cli.main import cli

    parser = argparse.ArgumentParser(description="Devcontainer build using pyinfra @local connector")
    parser.add_argument("--user", dest="setup_user", help="User to configure (default: current user)")
    args, unknown = parser.parse_known_args()

    if args.setup_user:
        os.environ["SETUP_USER"] = args.setup_user

    with tempfile.NamedTemporaryFile(delete_on_close=False, mode="w", suffix=".py") as tmpfile:
        if len(sys.orig_argv) > 1 and sys.orig_argv[1] == "-c":
            tmpfile.write(sys.orig_argv[2])
            tmpfile.close()
            build_py = tmpfile.name
        elif len(sys.orig_argv) > 1:
            build_py = sys.orig_argv[1]
        else:
            with open(__file__) as f:
                tmpfile.write(f.read())
            tmpfile.close()
            build_py = tmpfile.name

        sys.argv = ["pyinfra", "@local", "-y", build_py]
        cli()

import getpass
import io
import os
import pathlib

from pyinfra.context import config, host
from pyinfra.facts.files import FileContents
from pyinfra.facts.server import LinuxDistribution
from pyinfra.operations import apt, files, python, server, systemd
from tenacity import retry, stop_after_attempt, wait_exponential

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


def get_bashrc():
    return io.StringIO(
        "\n".join(host.get_fact(FileContents, "/etc/skel/.bashrc"))
        + """
# Shell enhancements
eval "$(mise activate bash)"
eval "$(starship init bash)"
eval "$(zoxide init bash)"
"""
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def install_mise_tools(target_user: str):
    server.shell(
        name="Install mise tools",
        commands="mise install --yes",
        _env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
        _sudo=True,
        _su_user=target_user,
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

# Configure sudo and locale (atomic file creation with correct mode)
server.shell(
    name="Create sudoers file",
    commands=f"install -m 440 /dev/null /etc/sudoers.d/{user} && echo '{user} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{user}",
)
apt.packages(packages=["curl", "gnupg", "locales", "extrepo"], update=True)
server.locale(locale="en_US.UTF-8")

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

# Docker socket init script (fixes socket permissions only)
DOCKER_INIT = io.StringIO("""\
#!/bin/bash
# Determine socket path from DOCKER_HOST or default
if [ -n "$DOCKER_HOST" ]; then
    # Extract socket path from unix:// prefix
    SOCK="${DOCKER_HOST#unix://}"
    # Handle non-socket DOCKER_HOST (TCP, SSH) - nothing to fix
    if [[ ! "$SOCK" =~ ^/ ]]; then
        echo "DOCKER_HOST is not a Unix socket: $DOCKER_HOST"
        exit 0
    fi
else
    SOCK="/var/run/docker.sock"
fi

# Guard clause: Exit cleanly if socket missing
if [ ! -S "$SOCK" ]; then
    echo "No Docker socket found at $SOCK"
    exit 0
fi

# Fix Permissions
GID=$(stat -c '%g' "$SOCK")
sudo groupmod -g "$GID" docker 2>/dev/null \
    && echo "Updated Docker GID to $GID" \
    || echo "Docker GID check: Skipped (already set or permission denied)"

exit 0
""")
files.put(name="Docker init script", src=DOCKER_INIT, dest="/usr/local/bin/docker-init.sh")
files.file(path="/usr/local/bin/docker-init.sh", mode="755")

# Configure user groups and Docker service (for bare metal installs with systemd)
server.user(name="Configure groups", user=user, shell="/bin/bash", groups=["sudo", "docker"])
# Disable user-level docker service first (can conflict with system service), then enable systemwide
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
    install_mise_tools(user)

    # Shell configuration
    files.put(name="Shell extras", src=get_bashrc(), dest=f"{home}/.bashrc", _sudo_user=user)
    # Fix home directory ownership recursively
    server.shell(commands=f"find {home} -maxdepth 2 -type d -exec chown {user}:{user} {{}} \\;")


python.call(function=in_home)
