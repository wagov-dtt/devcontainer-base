"""Pyinfra deploy used by the wagov-devcontainer CLI."""

from __future__ import annotations

import getpass
import io
import os
import pathlib
import re
import shlex

from pyinfra.context import config, host
from pyinfra.facts.files import FileContents
from pyinfra.facts.server import LinuxDistribution
from pyinfra.operations import apt, files, python, server, systemd
from tenacity import retry, stop_after_attempt, wait_exponential

from wagov_devcontainer.spec import APT_PACKAGES, APT_REPOS, MISE_TOML

USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]*[$]?$")


def get_bashrc() -> io.StringIO:
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
def install_mise_tools(target_user: str) -> None:
    server.shell(
        name="Install mise tools",
        commands="mise install --yes",
        _env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
        _sudo=True,
        _su_user=target_user,
    )


config.SUDO = True

distro = host.get_fact(LinuxDistribution)
if distro and distro.get("name") == "Debian":
    version = distro.get("major", "")
    codename = distro.get("release_meta", {}).get("CODENAME", "")
    if codename != "trixie" and version != "13":
        print(f"Warning: This devcontainer is designed for Debian 13 (Trixie), but detected {distro.get('name')} {version} ({codename})")
        print("Consider upgrading to Debian Trixie for optimal compatibility")

user = os.getenv("SETUP_USER", getpass.getuser())
if not USERNAME_RE.fullmatch(user):
    raise ValueError(f"Invalid SETUP_USER value: {user!r}")

server.user(user=user, create_home=True)

server.shell(
    name="Create sudoers file",
    commands=f"install -m 440 /dev/null /etc/sudoers.d/{user} && echo '{user} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{user}",
)
apt.packages(packages=["curl", "gnupg", "locales", "extrepo"], update=True)
server.locale(locale="en_US.UTF-8")

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

for repo in APT_REPOS:
    server.shell(commands=f"extrepo enable {repo}")
apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True)

if pathlib.Path("/run/systemd/system").is_dir():
    apt.packages(name="Install Docker daemon (bare metal)", packages=["docker-ce", "containerd.io"])

server.shell(name="Ensure docker group", commands="groupadd -f docker")

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

server.user(name="Configure groups", user=user, shell="/bin/bash", groups=["sudo", "docker"])
systemd.service(service="docker", enabled=False, user_mode=True, _su_user=user, _ignore_errors=True)
systemd.service(service="docker", enabled=True, running=True, _ignore_errors=True)


def in_home(state, host):
    _status, _stdout = host.run_shell_command(f"getent passwd {user} | cut -d: -f6")
    home = _stdout.output.strip()

    files.directory(path=f"{home}/.config/mise", user=user, group=user, mode="755")
    files.block(
        name="Mise config",
        path=f"{home}/.config/mise/config.toml",
        try_prevent_shell_expansion=True,
        content=MISE_TOML,
    )
    files.file(path=f"{home}/.config/mise/config.toml", user=user, group=user, mode="644")
    install_mise_tools(user)

    files.put(name="Shell extras", src=get_bashrc(), dest=f"{home}/.bashrc", _sudo_user=user)
    server.shell(commands=f"find {shlex.quote(home)} -maxdepth 2 -type d -exec chown {user}:{user} {{}} \\;")


python.call(function=in_home)
