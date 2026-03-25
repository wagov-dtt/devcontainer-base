"""Pyinfra deploy used by the wagov-devcontainer CLI."""

from __future__ import annotations

import getpass
import io
import os
import pathlib
import re

from pyinfra.context import config, host
from pyinfra.facts.server import Home, LinuxDistribution
from pyinfra.operations import apt, files, python, server, systemd
from tenacity import retry, stop_after_attempt, wait_exponential

from wagov_devcontainer.spec import APT_PACKAGES, APT_REPOS, MISE_TOML

USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]*[$]?$")
BASHRC_MARKER = "# {mark} WAGOV DEVCONTAINER"
BASHRC_SNIPPET_NAME = "shell.sh"
SHELL_ENHANCEMENTS = """# Shell enhancements
command -v mise >/dev/null 2>&1 && eval "$(mise activate bash)"
command -v starship >/dev/null 2>&1 && eval "$(starship init bash)"
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash)"
"""


def build_bashrc_source_block(shell_snippet_path: str) -> str:
    return f'''# Load wagov devcontainer shell helpers
if [ -f "{shell_snippet_path}" ]; then
    . "{shell_snippet_path}"
fi
'''


DOCKER_INIT_SH = """#!/bin/sh
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
"""


def put_text_file(name: str, content: str, dest: str, *, mode: str, user: str | None = None, group: str | None = None) -> None:
    files.put(name=name, src=io.StringIO(content), dest=dest, user=user, group=group, mode=mode)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def install_mise_tools(target_user: str) -> None:
    env = {}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        env["GITHUB_TOKEN"] = github_token

    server.shell(
        name="Install mise tools",
        commands="mise install --yes",
        _env=env,
        _sudo=True,
        _su_user=target_user,
    )


def warn_if_unsupported_debian() -> None:
    distro = host.get_fact(LinuxDistribution)
    if not distro or distro.get("name") != "Debian":
        return

    version = distro.get("major", "")
    codename = distro.get("release_meta", {}).get("CODENAME", "")
    if codename == "trixie" or version == "13":
        return

    print(f"Warning: This devcontainer is designed for Debian 13 (Trixie), but detected {distro.get('name')} {version} ({codename})")
    print("Consider upgrading to Debian Trixie for optimal compatibility")


def get_setup_user() -> str:
    user = os.getenv("SETUP_USER", getpass.getuser())
    if not USERNAME_RE.fullmatch(user):
        raise ValueError(f"Invalid SETUP_USER value: {user!r}")
    return user


def install_bootstrap_packages() -> None:
    apt.packages(name="Install bootstrap packages", packages=["curl", "gnupg", "locales", "extrepo", "sudo"], update=True)
    server.locale(locale="en_US.UTF-8")


def configure_extrepo() -> None:
    files.line(name="Enable contrib policy", path="/etc/extrepo/config.yaml", line="# - contrib", replace="- contrib")
    files.line(name="Enable non-free policy", path="/etc/extrepo/config.yaml", line="# - non-free", replace="- non-free")

    for repo in APT_REPOS:
        server.shell(name=f"Enable extrepo repo {repo}", commands=f"extrepo enable {repo}")


def configure_user(target_user: str) -> None:
    server.group(name="Ensure docker group", group="docker")
    server.user(name="Ensure target user", user=target_user, create_home=True, shell="/bin/bash", groups=["sudo", "docker"], append=True)
    put_text_file(
        name="Configure passwordless sudo",
        content=f"{target_user} ALL=(ALL) NOPASSWD:ALL\n",
        dest=f"/etc/sudoers.d/{target_user}",
        mode="440",
    )


def install_docker_init_script() -> None:
    put_text_file(name="Docker init script", content=DOCKER_INIT_SH, dest="/usr/local/bin/docker-init.sh", mode="755")


# pyinfra python.call injects state/host.
def configure_home(state, host, username: str) -> None:
    home = host.get_fact(Home, username) or ("/root" if username == "root" else f"/home/{username}")
    config_dir = f"{home}/.config"
    mise_dir = f"{config_dir}/mise"
    shell_snippet_path = f"{config_dir}/{BASHRC_SNIPPET_NAME}"
    bashrc_path = f"{home}/.bashrc"

    files.directory(name="Ensure user config directory", path=config_dir, user=username, group=username, mode="755")
    files.directory(name="Ensure mise config directory", path=mise_dir, user=username, group=username, mode="755")
    put_text_file(
        name="Mise config",
        content=MISE_TOML,
        dest=f"{mise_dir}/config.toml",
        user=username,
        group=username,
        mode="644",
    )
    put_text_file(
        name="Shell snippet",
        content=SHELL_ENHANCEMENTS,
        dest=shell_snippet_path,
        user=username,
        group=username,
        mode="644",
    )
    files.block(
        name="Source shell snippet from bashrc",
        path=bashrc_path,
        marker=BASHRC_MARKER,
        content=build_bashrc_source_block(shell_snippet_path),
    )
    files.file(path=bashrc_path, user=username, group=username, mode="644")
    install_mise_tools(username)


config.SUDO = True

warn_if_unsupported_debian()
user = get_setup_user()
install_bootstrap_packages()
configure_user(user)
configure_extrepo()
apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True)

if pathlib.Path("/run/systemd/system").is_dir():
    apt.packages(name="Install Docker daemon (bare metal)", packages=["docker-ce", "containerd.io"])

install_docker_init_script()
systemd.service(service="docker", enabled=False, user_mode=True, _su_user=user, _ignore_errors=True)
systemd.service(service="docker", enabled=True, running=True, _ignore_errors=True)
python.call(name="Configure user home", function=configure_home, username=user)
