"""Package metadata and tool definitions for the wagov devcontainer."""

from __future__ import annotations

import json
import re

BARE_TOML_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")

APT_REPOS = [
    "docker-ce",
    "github-cli",
    "kubernetes",
    "google_cloud",
    "ddev",
    "mise",
    "hashicorp",
]

APT_PACKAGES = [
    # Core tooling
    "docker-ce-cli",
    "docker-buildx-plugin",
    "docker-compose-plugin",
    "git",
    "neovim",
    "build-essential",
    "python3-dev",
    # Vendor/distribution packages
    "mise",
    "gh",
    "terraform",
    "ddev",
    "kubectl",
    # Shell and utilities
    "tini",
    "openssh-client",
    "bash-completion",
    "ripgrep",
    "ugrep",
    "fd-find",
    "bat",
    "jq",
    "less",
    "unzip",
    "zip",
    "file",
    "rsync",
    "librsvg2-bin",
    # Diagnostics and networking
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

BREW_PACKAGES = [
    # Base user-space toolchain for non-Debian brew hosts.
    "mise",
    "gh",
    "ripgrep",
    "ugrep",
    "fd",
    "bat",
    "yq",
    "starship",
    "zoxide",
    "eza",
    "direnv",
    # Additional repo-required compatibility packages where available.
    "btop",
    "ddev/ddev/ddev",
    "hashicorp/tap/terraform",
    "kubectl",
    "librsvg",
    "neovim",
    "tini",
]

MISE_SETTINGS = {
    "lockfile": True,
    "pipx.uvx": True,
    "python.compile": False,
    "trusted_config_paths": ["/workspaces"],
}

MISE_TOOLS = {
    # Languages and package managers
    "go": "latest",
    "node": "latest",
    "python": "latest",
    "pnpm": "latest",
    "uv": "latest",
    "pipx": "latest",
    "cargo-binstall": "latest",
    # Cloud and platform tooling
    "aws-cli": "latest",
    "aws-sam": "latest",
    "localstack": "latest",
    "helm": "latest",
    "kustomize": "latest",
    "k9s": "latest",
    "k3d": "latest",
    "tflint": "latest",
    "terraform-docs": "latest",
    "vault": "latest",
    # Supply chain and security
    "cosign": "latest",
    "slsa-verifier": "latest",
    "semgrep": "latest",
    "lychee": "latest",
    # Shell and developer UX
    "just": "latest",
    "zellij": "latest",
    "lazygit": "latest",
    "hurl": "latest",
    "envsubst": "latest",
    # Additional package sources
    "pipx:tldr": "latest",
    "pipx:httpie": "latest",
    "cargo:mdbook": "latest",
    "npm:@devcontainers/cli": "latest",
    "rumdl": "latest",
    "github:boyter/scc": "latest",
}


def render_toml_key(key: str) -> str:
    return key if BARE_TOML_KEY_RE.fullmatch(key) else json.dumps(key)


def render_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        return f"[{', '.join(render_toml_value(item) for item in value)}]"
    if isinstance(value, dict):
        items = ", ".join(f"{render_toml_key(key)} = {render_toml_value(item)}" for key, item in value.items())
        return f"{{ {items} }}"
    raise TypeError(f"Unsupported TOML value: {value!r}")


def render_toml_table(name: str, values: dict[str, object]) -> str:
    lines = [f"[{name}]"]
    lines.extend(f"{render_toml_key(key)} = {render_toml_value(value)}" for key, value in values.items())
    return "\n".join(lines)


def build_mise_toml() -> str:
    return "\n\n".join((render_toml_table("settings", MISE_SETTINGS), render_toml_table("tools", MISE_TOOLS))) + "\n"


MISE_TOML = build_mise_toml()
