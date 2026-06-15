# Cloud Native Devcontainer

Production-ready development container with modern tooling for cloud-native and infrastructure development.

## What's Inside

**Languages**: [Go](https://go.dev), [Node.js](https://nodejs.org), [Python](https://python.org), [Rust](https://rust-lang.org), [uv](https://github.com/astral-sh/uv), [pnpm](https://pnpm.io), [aube](https://aube.en.dev)
**Cloud**: [AWS CLI](https://aws.amazon.com/cli/), [Terraform](https://terraform.io), Kubernetes ([kubectl](https://kubernetes.io/docs/reference/kubectl/), [k9s](https://k9scli.io), [k3d](https://k3d.io), [helm](https://helm.sh), [kustomize](https://kustomize.io))
**Development**: Docker-outside-of-Docker, [OpenCode](https://opencode.ai), [oy](https://github.com/wagov-dtt/oy-cli), [git](https://git-scm.com), [just](https://just.systems), [mise](https://mise.jdx.dev), [direnv](https://direnv.net), [starship](https://starship.rs), [zellij](https://zellij.dev), [neovim](https://neovim.io), [lazygit](https://github.com/jesseduffield/lazygit), [delta](https://github.com/dandavison/delta), [difftastic](https://difftastic.wilfred.me.uk)
**Security**: [Semgrep](https://semgrep.dev), [cosign](https://github.com/sigstore/cosign), [SLSA verifier](https://github.com/slsa-framework/slsa-verifier), [lychee](https://lychee.cli.rs) (link checker), [Trivy](https://trivy.dev), [Syft](https://github.com/anchore/syft), [sops](https://getsops.io), [age](https://age-encryption.org)
**Linting/formatting**: [ShellCheck](https://www.shellcheck.net), [shfmt](https://github.com/mvdan/sh), [actionlint](https://github.com/rhysd/actionlint), [taplo](https://taplo.tamasfe.dev), [typos](https://github.com/crate-ci/typos), [hadolint](https://github.com/hadolint/hadolint), [yamlfmt](https://github.com/google/yamlfmt)
**Utilities**: [ripgrep](https://github.com/BurntSushi/ripgrep), [fzf](https://github.com/junegunn/fzf), [jq](https://jqlang.github.io/jq/), [yq](https://mikefarah.gitbook.io/yq), [httpie](https://httpie.io), [hurl](https://hurl.dev), [btop](https://github.com/aristocratos/btop), [restic](https://restic.net), [rclone](https://rclone.org)

> **Complete list**: See [`mise.toml`](mise.toml) and [`mise.apt.toml`](mise.apt.toml)

## Quick Start

### VS Code Devcontainer (Recommended)

Create `.devcontainer/devcontainer.json`:
```json
{
  "name": "My Project",
  "image": "ghcr.io/wagov-dtt/devcontainer-base",
  "features": {
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {
      "moby": false,
      "dockerDashComposeVersion": "none"
    }
  },
  "remoteEnv": {
    "LOCAL_WORKSPACE_FOLDER": "${localWorkspaceFolder}"
  },
  "remoteUser": "vscode"
}
```

Open in VS Code: **Cmd/Ctrl+Shift+P** -> "Dev Containers: Reopen in Container"

<details>
<summary>Why these settings?</summary>

- `docker-outside-of-docker` - Reuses the host Docker socket without privileged mode and handles socket permissions/rootless setups more robustly than a manual bind mount.
- `moby: false` - Uses the Docker CLI already baked into this Debian stable-backports image. The feature's default Moby packages are not available on Debian Trixie.
- `dockerDashComposeVersion: "none"` - Avoids installing an extra `docker-compose` binary because `docker compose` is already included via `docker-compose-plugin`.
- `LOCAL_WORKSPACE_FOLDER` - Makes the host workspace path available for Docker bind mounts from inside the container.
- `remoteUser: vscode` - Correct user permissions

If you need compatibility with an older Docker daemon, set `DOCKER_API_VERSION` in `remoteEnv` as a project-specific workaround rather than by default.
</details>

#### Rootless Docker

For rootless Docker, override the feature's default socket mount to point at your user socket:

```json
{
  "name": "My Project",
  "image": "ghcr.io/wagov-dtt/devcontainer-base",
  "features": {
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {
      "moby": false,
      "dockerDashComposeVersion": "none"
    }
  },
  "mounts": [
    {
      "source": "/run/user/1000/docker.sock",
      "target": "/var/run/docker-host.sock",
      "type": "bind"
    }
  ],
  "remoteUser": "vscode"
}
```

Replace `1000` with `id -u` from your host.

#### Docker bind mounts from inside the devcontainer

Docker commands run against the host daemon, so bind-mount source paths must exist on the host. Use `LOCAL_WORKSPACE_FOLDER` when invoking Docker:

```bash
docker run --rm -v "${LOCAL_WORKSPACE_FOLDER}:/workspace" debian:stable-slim pwd
```

For projects with Docker Compose files that assume container paths match host paths, mount the workspace at the same absolute path:

```json
{
  "workspaceFolder": "${localWorkspaceFolder}",
  "workspaceMount": "source=${localWorkspaceFolder},target=${localWorkspaceFolder},type=bind"
}
```

This is not available when using VS Code's **Clone Repository in Container Volume** flow, because `${localWorkspaceFolder}` does not exist there.

### Docker CLI

The image still includes Docker CLI/buildx/compose for direct `docker run` usage outside VS Code Dev Containers:

```bash
# Basic usage (mount host Docker socket)
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --group-add $(stat -c '%g' /var/run/docker.sock) \
  ghcr.io/wagov-dtt/devcontainer-base

# With your projects mounted
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --group-add $(stat -c '%g' /var/run/docker.sock) \
  -v ~/projects:/workspaces \
  ghcr.io/wagov-dtt/devcontainer-base
```

### Install on Existing System

Works on Debian/Ubuntu (including Ubuntu 26.04) and brew-based hosts (macOS, atomic Linux).
Installs via [mise bootstrap](https://mise.jdx.dev/bootstrap.html) — no Python, pip, uv, or pyinfra required.

```bash
# One-liner: auto-detects APT or brew
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh

# Install for a specific user (requires root/sudo)
SETUP_USER=myuser curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh

# Clone and run locally
git clone https://github.com/wagov-dtt/devcontainer-base && cd devcontainer-base
sudo ./install.sh
```

**What it does:**

1. Installs [mise](https://mise.jdx.dev) if missing
2. Detects platform (APT for Debian/Ubuntu, brew for macOS/atomic)
3. Fetches `mise.toml` + platform-specific config (`mise.apt.toml` or `mise.brew.toml`)
4. Runs `mise bootstrap --yes -E <platform>`:
   - Installs system packages (Docker CLI, git, neovim, ripgrep, etc.)
   - Installs 60+ development tools (Go, Node, Python, k9s, Terraform, etc.)
   - Applies shell dotfiles (bashrc enhancements)

Set `GITHUB_TOKEN` to avoid API rate limits. The script auto-exports it from `gh auth token` when available.

To skip system packages and only install user-level tools, run manually:

```bash
mise trust --yes .
mise install --yes          # tools only, no system packages
mise dotfiles apply --yes   # shell config only
```

### Use as Template

1. **GitHub**: Click "Use this template" to create your own repository
2. **Codespaces**: Works immediately - click "Code" → "Create codespace"
3. **Local**: Clone and customize as needed

### Use in Custom Docker Images

Consume this project's mise bootstrap config to layer the same toolchain into your own `Dockerfile`.

For Debian/Ubuntu images, copy the config and run the APT variant:

```dockerfile
FROM debian:stable-backports

ARG DEBIAN_FRONTEND=noninteractive

COPY mise.toml mise.apt.toml ./

RUN apt-get update -y \
    && apt-get install -y curl ca-certificates extrepo gnupg locales sudo \
    && curl --proto '=https' --tlsv1.2 -sSf https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh \
    && sed -i 's/^# - contrib/- contrib/' /etc/extrepo/config.yaml \
    && sed -i 's/^# - non-free/- non-free/' /etc/extrepo/config.yaml \
    && for repo in docker-ce github-cli kubernetes google_cloud ddev mise hashicorp; do \
         extrepo enable "$repo" || echo "extrepo: $repo skipped or already enabled"; \
       done \
    && mise trust --yes . \
    && mise bootstrap packages install --yes --update -E apt \
    && mise bootstrap --yes
```

For brew-based images or base OSes, copy `mise.toml` + `mise.brew.toml` and run the brew variant:

```dockerfile
COPY mise.toml mise.brew.toml ./
RUN curl --proto '=https' --tlsv1.2 -sSf https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh \
    && mise trust --yes . \
    && mise bootstrap --yes -E brew
```

The `-E apt` flag loads `mise.apt.toml`; `-E brew` loads `mise.brew.toml`. If you want only mise-managed tools and dotfiles (no system packages), omit `-E ...` and run `mise bootstrap --yes`.

See the project [`Dockerfile`](Dockerfile) for the full build pipeline including extrepo setup, user creation, and Docker socket integration.

### CI/CD Integration

Run tests in the devcontainer for guaranteed consistency:

```yaml
- name: Run tests in devcontainer
  uses: devcontainers/ci@v0.3
  with:
    imageName: local/devcontainer
    push: never
    runCmd: |
      just test
      mise run lint
```

See [`.github/workflows/test-devcontainer.yml`](.github/workflows/test-devcontainer.yml) for complete example.

## How It Works

### Architecture

- **Base**: Debian stable-backports (currently Trixie/13)
- **Package Management**: APT for system tools, mise for development tools
- **Provisioning**: [mise bootstrap](https://mise.jdx.dev/bootstrap.html) handles all installation and configuration during Docker build or local install
- **Docker-outside-of-Docker**: Host socket reuse via the upstream Dev Containers feature; Docker CLI/buildx/compose are also pre-installed for plain `docker run` usage

### Tool Sources

Tools are installed from two package backends, with separate config files for each platform:

1. **APT via [extrepo](https://wiki.debian.org/ExtRepo)** — Signed packages from official repos (Debian/Ubuntu only)
   - Docker, GitHub CLI, Terraform, kubectl, mise
   - Configured in [`mise.apt.toml`](mise.apt.toml) under `[bootstrap.packages]`
2. **Homebrew** — User-space packages for macOS and atomic Linux hosts
   - ripgrep, gh, starship, neovim, kubectl, terraform
   - Configured in [`mise.brew.toml`](mise.brew.toml) under `[bootstrap.packages]`
3. **[mise](https://mise.jdx.dev)** — Cross-platform development tools (all platforms)
   - Languages (Go, Node, Python), cargo tools, npm packages
   - Configured in [`mise.toml`](mise.toml) under `[tools]`

mise selects the right backend at runtime via environment configs: `-E apt` loads `mise.apt.toml`, `-E brew` loads `mise.brew.toml`. The Dockerfile always uses `-E apt`; `install.sh` auto-detects.

### Key Features

- **Security**: SBOM, signed images, Semgrep in-container
- **Performance**: Multi-platform builds (amd64/arm64), layer caching
- **Flexibility**: mise auto-switches tool versions per project
- **Supply Chain**: Verified packages via extrepo

### Adding Tools

Edit the appropriate config file and add your tool:

```toml
# Development tools → mise.toml
[tools]
"pipx:your-tool" = "latest"         # pipx backend
"npm:your-tool" = "latest"          # npm/aube backend
"cargo:your-tool" = "latest"        # cargo-binstall backend
"github:user/repo" = "latest"      # GitHub release binary
your-tool = "latest"                # mise default registry

# System packages (APT) → mise.apt.toml
[bootstrap.packages]
"apt:your-package" = "latest"

# System packages (brew) → mise.brew.toml
[bootstrap.packages]
"brew:your-formula" = "latest"
```

For provisioning hooks (extrepo setup, Docker daemon), see the `[bootstrap.hooks]` section in [`mise.apt.toml`](mise.apt.toml).

### Optional Cloud CLIs

GCP CLI and Azure CLI are not installed by default (saves ~1 GB). Install them when needed:

```bash
# GCP CLI (repo already enabled via extrepo)
sudo apt-get update && sudo apt-get install -y google-cloud-cli

# Azure CLI (repo not available for Trixie, use pipx)
pipx install azure-cli
```

## Development Commands

```bash
just              # List all commands
just build        # Build test image
just test         # Test Docker-outside-of-Docker
just dev          # Interactive shell
just lint         # Lint project files
just fmt          # Format project files
just clean        # Clean up images
```

**For maintainers:**
```bash
just publish      # Multi-platform build + push
just shell        # Run published image interactively
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker not working | Ensure Docker is running and the host socket is available. For rootless Docker, override the socket mount as shown above. |
| Tool missing | Check `mise.toml` |
| Build fails | Run `just clean` then `just build` |
| Docker permission errors | Rebuild the devcontainer so the `docker-outside-of-docker` feature can refresh socket access. For direct `docker run`, pass `--group-add $(stat -c '%g' /var/run/docker.sock)`. |
| mise issues | Run `mise doctor` inside container |

## Contributing

1. Fork and clone the repo
2. Make changes to `mise.toml`, `Dockerfile`, or docs
3. Test: `just build && just test && just dev`
4. Submit PR with test results

**What to contribute:**
- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance optimisations

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidance and project philosophy.
