#!/usr/bin/env python3
"""
Devcontainer build using pyinfra local connector.
Can be executed with: pipx run pyinfra @local -y build.py
Or via curl: curl -sSL <url>/build.py | pipx run pyinfra @local -y /dev/stdin

Environment variables:
- SETUP_USER: User to configure (default: current user)
"""

import getpass
import os
from io import StringIO

from pyinfra import host
from pyinfra.facts.server import Users
from pyinfra.operations import apt, files, server

# APT repositories configuration
APT_REPOS = [
    ("ddev", "https://pkg.ddev.com/apt/gpg.key", "https://pkg.ddev.com/apt/ * *"),
    ("charm", "https://repo.charm.sh/apt/gpg.key", "https://repo.charm.sh/apt/ * *"),
    ("mise", "https://mise.jdx.dev/gpg-key.pub", "https://mise.jdx.dev/deb stable main"),
    ("helm", "https://baltocdn.com/helm/signing.asc", "https://baltocdn.com/helm/stable/debian/ all main"),
    ("hashicorp", "https://apt.releases.hashicorp.com/gpg", "https://apt.releases.hashicorp.com bookworm main"),
    (
        "gcloud",
        "https://packages.cloud.google.com/apt/doc/apt-key.gpg",
        "https://packages.cloud.google.com/apt cloud-sdk main",
    ),
    (
        "github",
        "https://cli.github.com/packages/githubcli-archive-keyring.gpg",
        "https://cli.github.com/packages stable main",
    ),
    (
        "docker",
        "https://download.docker.com/linux/debian/gpg",
        "https://download.docker.com/linux/debian trixie stable",
    ),
    (
        "microsoft",
        "https://packages.microsoft.com/keys/microsoft.asc",
        "https://packages.microsoft.com/repos/azure-cli/ bookworm main",
    ),
]

# APT packages configuration
APT_PACKAGES = (
    ["docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin", "mise"]
    + ["ripgrep", "ugrep", "btop", "htop", "restic", "rclone", "crush", "git", "wget", "bash-completion"]
    + ["azure-cli", "google-cloud-cli", "gh", "ddev", "terraform", "helm", "neovim", "fzf"]
    + ["sudo", "python3-dev", "tini", "build-essential", "openssh-client", "less", "jq"]
    + ["unzip", "zip", "file", "rsync", "iputils-ping", "dnsutils", "net-tools"]
    + ["procps", "lsof", "locales", "librsvg2-bin", "iptables", "cosign"]
)

# Mise tools configuration
MISE_TOOLS = (
    ["go", "node", "python", "pnpm", "uv", "pipx", "just", "yq", "aws-cli", "aws-sam", "kubectl", "k9s"]
    + ["k3d", "kustomize", "tflint", "terraform-docs", "trivy", "vault", "zellij", "starship", "zoxide", "eza"]
    + ["direnv", "lazygit", "hurl", "lychee", "semgrep", "localstack", "pipx:tldr", "pipx:httpie"]
    + ["cargo:mdbook", "npm:@devcontainers/cli", "cargo-binstall", "ubi:rvben/rumdl", "ubi:boyter/scc"]
)

# Get setup user from environment or current user
user = os.getenv("SETUP_USER", getpass.getuser())
server.user(user=user, create_home=True, _sudo=True)
home = f"/home/{user}"
# Passwordless sudo
files.block(content=f"{user} ALL=(ALL) NOPASSWD:ALL", path=f"/etc/sudoers.d/{user}", _sudo=True)
files.file(path=f"/etc/sudoers.d/{user}", mode=440, _sudo=True)


# Combined repository and GPG key setup
def add_repo(repo_data):
    """Add GPG key and repository in one function."""
    name, key_url, deb_info = repo_data
    repo = apt.repo(src=f"deb [signed-by=/etc/apt/keyrings/{name}.gpg] {deb_info}", filename=name, _sudo=True)
    server.shell(
        commands=f"curl -fsSL {key_url} | gpg --dearmor --yes -o /etc/apt/keyrings/{name}.gpg",
        _sudo=True,
        _if=repo.did_change,
    )


apt.packages(packages=["curl", "gnupg", "locales"], update=True, _sudo=True)
server.locale("en_US.UTF-8")
files.directory(name="Create keyrings directory", path="/etc/apt/keyrings", mode="755", _sudo=True)
for repo in APT_REPOS:
    add_repo(repo)
apt.packages(name="Install apt packages", packages=APT_PACKAGES, update=True, upgrade=True, _sudo=True)
server.shell(
    name="Flip to legacy iptables to support docker in docker",
    commands=[
        "update-alternatives --set iptables /usr/sbin/iptables-legacy",
        "update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy",
    ],
    _sudo=True,
)
server.user(name="Add user to groups", user=user, shell="/bin/bash", groups=["sudo", "docker"], _sudo=True)

# Mise config/install
files.directory(path=f"{home}/.config/mise", user=user, group=user, mode="755")
files.block(
    name="Mise config",
    content=f"""
[settings]
python.compile = false
pipx.uvx = true
trusted_config_paths = ["/workspaces"]

[tools]
{"\n".join([f'"{tool}" = "latest"' for tool in MISE_TOOLS])}
""",
    path=f"{home}/.config/mise/config.toml",
    try_prevent_shell_expansion=True,
)
files.file(path=f"{home}/.config/mise/config.toml", user=user, group=user, mode="644")
server.shell(
    commands="mise install --yes",
    _env={
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        "COSIGN_EXPERIMENTAL": "0",
    },
    _su_user=user
)

files.block(
    name="Enhanced shell and docker startup",
    path=f"{home}/.bashrc",
    content="""
# Shell enhancements
eval "$(mise activate bash)"
eval "$(starship init bash)"
mise reshim

# Docker-in-Docker initialization
start_docker() {
    if ! test -r /proc/1/cgroup 2>/dev/null; then return 0; fi
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
""",
    try_prevent_shell_expansion=True,
    _sudo_user=user,
)
