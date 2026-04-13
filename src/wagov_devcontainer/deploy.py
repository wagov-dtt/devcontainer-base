"""Pyinfra deploy used by the wagov-devcontainer CLI."""

from __future__ import annotations

import getpass
import grp
import io
import os
import pathlib
import pwd
import re
import shutil

from pyinfra.context import config
from pyinfra.facts.server import Home
from pyinfra.operations import apt, files, python, server, systemd
from tenacity import retry, stop_after_attempt, wait_exponential

from wagov_devcontainer.spec import APT_PACKAGES, APT_REPOS, BREW_PACKAGES, MISE_TOML

USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]*[$]?$")
BASHRC_MARKER = "# {mark} WAGOV DEVCONTAINER"
BASHRC_SNIPPET_NAME = "shell.sh"
ATOMIC_HOST_IDS = {"aurora", "bazzite", "bluefin", "bootc", "kinoite", "ostree", "sericea", "silverblue"}
BREWFILE_PATH = pathlib.Path("/tmp/wagov-devcontainer-brew.Brewfile")
SHELL_ENHANCEMENTS = """# Shell enhancements
command -v mise >/dev/null 2>&1 && eval "$(mise activate bash)"
command -v starship >/dev/null 2>&1 && eval "$(starship init bash)"
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash)"
"""
BREW_HOST_SHELL_SNIPPET = "# Shell integration is managed by host-installed brew tools\n"
BREW_FORMULA_COMMANDS = {
    "mise": ("mise",),
    "gh": ("gh",),
    "ripgrep": ("rg",),
    "ugrep": ("ug", "ugrep"),
    "fd": ("fd",),
    "bat": ("bat",),
    "yq": ("yq",),
    "starship": ("starship",),
    "zoxide": ("zoxide",),
    "eza": ("eza",),
    "direnv": ("direnv",),
    "btop": ("btop",),
    "ddev/ddev/ddev": ("ddev",),
    "hashicorp/tap/terraform": ("terraform",),
    "kubectl": ("kubectl",),
    "librsvg": ("rsvg-convert",),
    "neovim": ("nvim",),
    "tini": ("tini",),
}


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


def read_os_release() -> dict[str, str]:
    for path in (pathlib.Path("/etc/os-release"), pathlib.Path("/usr/lib/os-release")):
        if not path.is_file():
            continue

        data = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            data[key] = value.strip().strip("\"'")

        return data

    return {}



def get_host_ids(os_release: dict[str, str]) -> set[str]:
    values = {
        os_release.get("ID", ""),
        os_release.get("IMAGE_ID", ""),
        os_release.get("VARIANT_ID", ""),
        *os_release.get("ID_LIKE", "").split(),
    }
    return {value.casefold() for value in values if value}



def get_host_name(os_release: dict[str, str]) -> str:
    return os_release.get("PRETTY_NAME") or os_release.get("NAME") or "this system"



def is_debian_family_host(os_release: dict[str, str]) -> bool:
    host_ids = get_host_ids(os_release)
    return "debian" in host_ids or "ubuntu" in host_ids



def is_atomic_host(os_release: dict[str, str]) -> bool:
    return pathlib.Path("/run/ostree-booted").exists() or bool(ATOMIC_HOST_IDS & get_host_ids(os_release))



def can_manage_system_packages(os_release: dict[str, str]) -> bool:
    return pathlib.Path("/usr/bin/apt-get").exists() and is_debian_family_host(os_release)



def get_setup_user() -> str:
    user = os.getenv("SETUP_USER", getpass.getuser())
    if not USERNAME_RE.fullmatch(user):
        raise ValueError(f"Invalid SETUP_USER value: {user!r}")
    return user



def require_existing_user(username: str, os_release: dict[str, str]) -> None:
    try:
        pwd.getpwnam(username)
    except KeyError as exc:
        raise ValueError(f"User {username!r} does not exist on {get_host_name(os_release)}") from exc



def get_user_home(username: str) -> str:
    return pwd.getpwnam(username).pw_dir



def get_primary_group(username: str) -> str:
    return grp.getgrgid(pwd.getpwnam(username).pw_gid).gr_name



def get_run_as_target_user_kwargs(target_user: str) -> dict[str, object]:
    if target_user == getpass.getuser():
        return {}
    return {"_sudo": True, "_su_user": target_user}



def put_text_file(name: str, content: str, dest: str, *, mode: str, user: str | None = None, group: str | None = None) -> None:
    files.put(name=name, src=io.StringIO(content), dest=dest, user=user, group=group, mode=mode)



def local_command_exists(command: str) -> bool:
    return shutil.which(command) is not None



def is_brew_host() -> bool:
    return local_command_exists("brew")



def is_brew_formula_needed(formula: str) -> bool:
    commands = BREW_FORMULA_COMMANDS.get(formula)
    if not commands:
        return True
    return not any(local_command_exists(command) for command in commands)



def get_missing_brew_packages() -> list[str]:
    return [formula for formula in BREW_PACKAGES if is_brew_formula_needed(formula)]



def render_brewfile() -> str:
    missing_packages = get_missing_brew_packages()
    if not missing_packages:
        return ""
    lines = [f'brew "{package}"' for package in missing_packages]
    return "\n".join(lines) + "\n"



def install_brew_compat_packages(target_user: str) -> None:
    content = render_brewfile()
    if not content:
        print("Brew compatibility packages already satisfied")
        return

    put_text_file(
        name="Brew compatibility Brewfile",
        content=content,
        dest=str(BREWFILE_PATH),
        mode="644",
        user=target_user,
        group=get_primary_group(target_user),
    )
    server.shell(
        name="Install brew compatibility packages",
        commands=f"brew bundle --file={BREWFILE_PATH}",
        **get_run_as_target_user_kwargs(target_user),
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def install_mise_tools(target_user: str) -> None:
    env = {}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        env["GITHUB_TOKEN"] = github_token

    server.shell(
        name="Install mise tools",
        commands="if command -v mise >/dev/null 2>&1; then mise install --yes; else echo 'Skipping mise install: mise not found on PATH'; fi",
        _env=env,
        **get_run_as_target_user_kwargs(target_user),
    )



def warn_if_unsupported_debian(os_release: dict[str, str]) -> None:
    if not is_debian_family_host(os_release):
        return

    version = os_release.get("VERSION_ID", "")
    codename = os_release.get("VERSION_CODENAME", "").casefold()
    if codename == "trixie" or version == "13":
        return

    print(f"Warning: This devcontainer is designed for Debian 13 (Trixie), but detected {get_host_name(os_release)}")
    print("Continuing with APT-based provisioning")



def warn_if_user_space_only_host(os_release: dict[str, str]) -> None:
    host_name = get_host_name(os_release)
    if is_atomic_host(os_release):
        print(f"Detected atomic/ostree host: {host_name}")
        print("Skipping APT/extrepo, user creation, Docker daemon, and systemd changes; configuring the target user's home only")
        return

    if is_brew_host():
        print(f"Detected brew-based host: {host_name}")
        print("Skipping APT/extrepo, user creation, Docker daemon, and systemd changes; using brew for user-space tooling")
        return

    print(f"Warning: APT-based provisioning is unavailable on {host_name}")
    print("Falling back to user-space setup only; install any required system packages separately")



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
def configure_home(state, host, username: str, prefer_host_shell_integration: bool = False) -> None:
    home = host.get_fact(Home, username) or get_user_home(username)
    primary_group = get_primary_group(username)
    config_dir = f"{home}/.config"
    mise_dir = f"{config_dir}/mise"
    shell_snippet_path = f"{config_dir}/{BASHRC_SNIPPET_NAME}"
    bashrc_path = f"{home}/.bashrc"
    shell_content = BREW_HOST_SHELL_SNIPPET if prefer_host_shell_integration else SHELL_ENHANCEMENTS

    files.directory(name="Ensure user config directory", path=config_dir, user=username, group=primary_group, mode="755")
    files.directory(name="Ensure mise config directory", path=mise_dir, user=username, group=primary_group, mode="755")
    put_text_file(
        name="Mise config",
        content=MISE_TOML,
        dest=f"{mise_dir}/config.toml",
        user=username,
        group=primary_group,
        mode="644",
    )
    put_text_file(
        name="Shell snippet",
        content=shell_content,
        dest=shell_snippet_path,
        user=username,
        group=primary_group,
        mode="644",
    )
    files.block(
        name="Source shell snippet from bashrc",
        path=bashrc_path,
        marker=BASHRC_MARKER,
        content=build_bashrc_source_block(shell_snippet_path),
    )
    files.file(path=bashrc_path, user=username, group=primary_group, mode="644")
    install_mise_tools(username)


os_release = read_os_release()
user = get_setup_user()
prefer_host_shell_integration = False

if can_manage_system_packages(os_release):
    config.SUDO = True
    warn_if_unsupported_debian(os_release)
    install_bootstrap_packages()
    configure_user(user)
    configure_extrepo()
    apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True)

    if pathlib.Path("/run/systemd/system").is_dir():
        apt.packages(name="Install Docker daemon (bare metal)", packages=["docker-ce", "containerd.io"])

    install_docker_init_script()
    systemd.service(service="docker", enabled=False, user_mode=True, _su_user=user, _ignore_errors=True)
    systemd.service(service="docker", enabled=True, running=True, _ignore_errors=True)
else:
    config.SUDO = user != getpass.getuser()
    require_existing_user(user, os_release)
    prefer_host_shell_integration = is_brew_host()
    if prefer_host_shell_integration:
        install_brew_compat_packages(user)
    warn_if_user_space_only_host(os_release)

python.call(
    name="Configure user home",
    function=configure_home,
    username=user,
    prefer_host_shell_integration=prefer_host_shell_integration,
)
