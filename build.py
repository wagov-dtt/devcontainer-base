#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
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
import os

from pyinfra import config, host
from pyinfra.facts.server import LinuxDistribution, Users
from pyinfra.operations import apt, files, python, server, systemd

# APT repositories (extrepo where available, manual otherwise)
APT_REPOS = [
    # extrepo-managed (secure & standardised)
    ("docker-ce", None, "extrepo"),
    ("github-cli", None, "extrepo"),
    ("kubernetes", None, "extrepo"),
    ("google_cloud", None, "extrepo"),
    # Manual repositories (not in extrepo)
    ("ddev", "https://pkg.ddev.com/apt/gpg.key", "https://pkg.ddev.com/apt/ * *"),
    ("charm", "https://repo.charm.sh/apt/gpg.key", "https://repo.charm.sh/apt/ * *"),
    ("mise", "https://mise.jdx.dev/gpg-key.pub", "https://mise.jdx.dev/deb stable main"),
    ("hashicorp", "https://apt.releases.hashicorp.com/gpg", "https://apt.releases.hashicorp.com bookworm main"),
    ("microsoft", "https://packages.microsoft.com/keys/microsoft.asc", "https://packages.microsoft.com/repos/azure-cli/ bookworm main"),
]

# APT packages configuration
APT_PACKAGES = (
    # Container & Development
    ["extrepo", "docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin", "git", "neovim", "build-essential", "python3-dev"]
    # Cloud & Infrastructure
    + ["azure-cli", "google-cloud-cli", "gh", "terraform", "ddev", "kubectl", "kustomize"]
    # System & Utilities
    + ["sudo", "tini", "openssh-client", "bash-completion", "locales", "iptables", "ripgrep", "ugrep", "jq", "less", "unzip", "zip", "file", "rsync", "librsvg2-bin"]
    # Monitoring & Network Tools
    + ["btop", "htop", "procps", "lsof", "iputils-ping", "dnsutils", "net-tools", "restic", "rclone", "crush", "wget", "fzf"]
    # Tool Managers
    + ["mise"]
)

# Mise tools configuration
MISE_TOOLS = (
    # Languages & Package Management
    ["go", "node", "python", "pnpm", "uv", "pipx", "cargo-binstall", "ubi:railwayapp/railpack"]
    # Cloud & Infrastructure
    + ["aws-cli", "aws-sam", "localstack", "helm", "k9s", "k3d", "terraform", "tflint", "terraform-docs", "vault"]
    # Security & Quality
    + ["trivy", "cosign", "slsa-verifier", "semgrep", "lychee"]
    # Shell & Development Tools
    + ["just", "yq", "zellij", "starship", "zoxide", "eza", "direnv", "lazygit", "hurl", "envsubst"]
    # Documentation & Utilities
    + ["pipx:tldr", "pipx:httpie", "cargo:mdbook", "npm:@devcontainers/cli", "ubi:rvben/rumdl", "ubi:boyter/scc"]
)

MISE_TOML = f"""
[settings]
lockfile = true
pipx.uvx = true
python.compile = false
trusted_config_paths = ["/workspaces"]

[tools]
{"\n".join([f'"{tool}" = "latest"' for tool in MISE_TOOLS])}
"""

BASHRC_EXTRAS = """
# Shell enhancements
eval "$(mise activate bash)"
eval "$(starship init bash)"
mise reshim

# Docker-in-Docker initialization
start_docker() {
    if test -d /run/systemd/system; then return 0; fi
    if pgrep -x dockerd >/dev/null 2>&1; then return 0; fi
    find /var/run -name "docker*.pid" -delete 2>/dev/null || true
    sudo dockerd >/tmp/dockerd.log 2>&1 &
    local timeout=5
    while ((timeout-- > 0)); do
        if docker version >/dev/null 2>&1; then return 0; fi
        sleep 1
    done
    echo "Error: Docker failed to start within 5 seconds" >&2
    return 1
}
start_docker
"""

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
files.line(name="Enable contrib policy", path="/etc/extrepo/config.yaml", line="# - contrib", replace="- contrib")
files.line(name="Enable non-free policy", path="/etc/extrepo/config.yaml", line="# - non-free", replace="- non-free")

# Setup repositories (extrepo & manual)
files.directory(name="Create keyrings directory", path="/etc/apt/keyrings", mode="755")
for name, key_url, deb_info in APT_REPOS:
    if deb_info == "extrepo":
        # Use extrepo for secure & standardised repos
        server.shell(commands=f"extrepo enable {name}")
    else:
        # Manual repository setup
        repo = apt.repo(src=f"deb [signed-by=/etc/apt/keyrings/{name}.gpg] {deb_info}", filename=name)
        server.shell(commands=f"curl -fsSL {key_url} | gpg --dearmor --yes -o /etc/apt/keyrings/{name}.gpg", _if=repo.did_change)
apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True)

# Configure systemctl for rootful Docker (ignore failures if no systemd)
server.user(name="Configure groups", user=user, shell="/bin/bash", groups=["sudo", "docker"])
systemd.service(service="docker", enabled=False, user_mode=True, _su_user=user, _ignore_errors=True)
docker_systemd = systemd.service(service="docker", enabled=True, running=True, _ignore_errors=True)

# Use legacy iptables only in container environments (when systemd docker service failed)
server.shell(
    name="iptables-legacy (container mode)",
    commands=["update-alternatives --set iptables /usr/sbin/iptables-legacy", "update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy"],
    _if=docker_systemd.did_error,
)


# Configure home dir
def in_home(state, host):
    _status, _stdout = host.run_shell_command(f"getent passwd {user} | cut -d: -f6")
    home = _stdout.output.strip()

    # Mise config/install
    files.directory(path=f"{home}/.config/mise", user=user, group=user, mode="755")
    files.block(name="Mise config", path=f"{home}/.config/mise/config.toml", try_prevent_shell_expansion=True, content=MISE_TOML)
    files.file(path=f"{home}/.config/mise/config.toml", user=user, group=user, mode="644")
    server.shell(commands="mise install --yes", _env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")}, _sudo=True, _su_user=user)

    # Shell & docker configuration
    files.block(name="Shell extras", path=f"{home}/.bashrc", content=BASHRC_EXTRAS, try_prevent_shell_expansion=True, _sudo_user=user)
    # Fix home directory ownership recursively
    server.shell(commands=f"find {home} -maxdepth 2 -type d -exec chown {user}:{user} {{}} \\;")


python.call(function=in_home)
