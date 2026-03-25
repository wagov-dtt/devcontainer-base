"""Package metadata and tool definitions for the wagov devcontainer."""

from __future__ import annotations

APT_REPOS = [
    "docker-ce",
    "github-cli",
    "kubernetes",
    "google_cloud",
    "ddev",
    "mise",
    "hashicorp",
]

APT_PACKAGES = (
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
    + [
        "mise",
        "gh",
        "terraform",
        "ddev",
        "kubectl",
    ]
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

MISE_TOOLS = (
    [
        "go",
        "node",
        "python",
        "pnpm",
        "uv",
        "pipx",
        "cargo-binstall",
    ]
    + [
        "aws-cli",
        "aws-sam",
        "localstack",
        "helm",
        "kustomize",
        "k9s",
        "k3d",
        "tflint",
        "terraform-docs",
        "vault",
    ]
    + ["github:aquasecurity/trivy", "cosign", "slsa-verifier", "semgrep", "lychee"]
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
    + [
        "pipx:tldr",
        "pipx:httpie",
        "cargo:mdbook",
        "npm:@devcontainers/cli",
        "rumdl",
        "github:boyter/scc",
    ]
)


def format_mise_tool(tool: str | tuple[str, str]) -> str:
    if isinstance(tool, str):
        return f'"{tool}" = "latest"'
    if isinstance(tool, tuple):
        name, config = tool
        return f'"{name}" = {config}'
    raise TypeError(f"Unexpected tool type: {type(tool)}")


MISE_TOOL_LINES = "\n".join(format_mise_tool(tool) for tool in MISE_TOOLS)

MISE_TOML = f"""[settings]
lockfile = true
pipx.uvx = true
python.compile = false
trusted_config_paths = ["/workspaces"]

[tools]
{MISE_TOOL_LINES}
"""
