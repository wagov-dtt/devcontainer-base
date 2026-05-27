# Cloud Native Devcontainer

Production-ready development container with modern tooling for cloud-native and infrastructure development.

## What's Inside

**Languages**: [Go](https://go.dev), [Node.js](https://nodejs.org), [Python](https://python.org), [Rust](https://rust-lang.org) (via [cargo-binstall](https://github.com/cargo-bins/cargo-binstall)), [uv](https://github.com/astral-sh/uv), [pnpm](https://pnpm.io), [aube](https://aube.en.dev)  
**Cloud**: [AWS CLI](https://aws.amazon.com/cli/), [Terraform](https://terraform.io), Kubernetes ([kubectl](https://kubernetes.io/docs/reference/kubectl/), [k9s](https://k9scli.io), [k3d](https://k3d.io), [helm](https://helm.sh), [kustomize](https://kustomize.io))  
**Development**: Docker-outside-of-Docker, [OpenCode](https://opencode.ai), [oy](https://github.com/wagov-dtt/oy-cli), [git](https://git-scm.com), [just](https://just.systems), [mise](https://mise.jdx.dev), [direnv](https://direnv.net), [starship](https://starship.rs), [zellij](https://zellij.dev), [neovim](https://neovim.io), [lazygit](https://github.com/jesseduffield/lazygit), [delta](https://github.com/dandavison/delta), [difftastic](https://difftastic.wilfred.me.uk)  
**Security**: [Semgrep](https://semgrep.dev), [cosign](https://github.com/sigstore/cosign), [SLSA verifier](https://github.com/slsa-framework/slsa-verifier), [lychee](https://lychee.cli.rs) (link checker), [Trivy](https://trivy.dev), [Syft](https://github.com/anchore/syft), [sops](https://getsops.io), [age](https://age-encryption.org)  
**Linting/formatting**: [ShellCheck](https://www.shellcheck.net), [shfmt](https://github.com/mvdan/sh), [actionlint](https://github.com/rhysd/actionlint), [taplo](https://taplo.tamasfe.dev), [typos](https://github.com/crate-ci/typos), [hadolint](https://github.com/hadolint/hadolint), [yamlfmt](https://github.com/google/yamlfmt)  
**Utilities**: [ripgrep](https://github.com/BurntSushi/ripgrep), [fzf](https://github.com/junegunn/fzf), [jq](https://jqlang.github.io/jq/), [yq](https://mikefarah.gitbook.io/yq), [httpie](https://httpie.io), [hurl](https://hurl.dev), [btop](https://github.com/aristocratos/btop), [restic](https://restic.net), [rclone](https://rclone.org)

> **Complete list**: See [`src/wagov_devcontainer/spec.py`](src/wagov_devcontainer/spec.py) and [`src/wagov_devcontainer/deploy.py`](src/wagov_devcontainer/deploy.py)

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

Open in VS Code: **Cmd/Ctrl+Shift+P** → "Dev Containers: Reopen in Container"

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

Works on Debian/Ubuntu, including Ubuntu 26.04. On atomic or other brew-based hosts, the pyinfra deploy can use Homebrew for user-space tooling instead of attempting APT/extrepo or Docker daemon changes.

For direct `uvx`/`pipx run` usage, install these first:

- [GitHub CLI](https://cli.github.com/) (`gh`)
- either [uv](https://docs.astral.sh/uv/) (`uvx`) or [pipx](https://pipx.pypa.io/)

To avoid GitHub API rate limits during tool installs, export a token from `gh` first:

```bash
export GITHUB_TOKEN="$(gh auth token)"

# Preferred: run the published package directly
uvx wagov-devcontainer

# Or with pipx
pipx run --spec wagov-devcontainer wagov-devcontainer

# Repo helper script for Debian/Ubuntu, including Ubuntu 26.04
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
```

The helper script also auto-detects `GITHUB_TOKEN` from `gh auth token` when `gh` is installed.
On non-APT hosts, use `uvx` or `pipx run` directly; the helper script will not try to bootstrap packages there. If `brew` is on `PATH`, the deploy installs the needed user-space packages itself and then runs `mise install --yes` once `mise` is available.

### Use as Template

1. **GitHub**: Click "Use this template" to create your own repository
2. **Codespaces**: Works immediately - click "Code" → "Create codespace"
3. **Local**: Clone and customize as needed

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
- **Build**: Python package (`wagov-devcontainer`) runs a pyinfra deploy during Docker build or local install
- **Docker-outside-of-Docker**: Host socket reuse via the upstream Dev Containers feature; Docker CLI/buildx/compose are also pre-installed for plain `docker run` usage

### Tool Sources

Tools are installed from two sources, preferring APT when available:

1. **APT via [extrepo](https://wiki.debian.org/ExtRepo)** (preferred) - Signed packages from official repos
   - Docker, GitHub CLI, Terraform, kubectl, mise
2. **[mise](https://mise.jdx.dev)** - Cross-platform tools not in APT, or needing version flexibility
   - Languages (Go, Node, Python), k9s, starship
   - npm-backed tools are installed through [aube](https://aube.en.dev) (`npm.package_manager = "aube"`)
   - Cargo-backed tools use [cargo-binstall](https://github.com/cargo-bins/cargo-binstall) when prebuilt binaries are available

### Key Features

- **Security**: SBOM, signed images, Semgrep in-container
- **Performance**: Multi-platform builds (amd64/arm64), layer caching
- **Flexibility**: mise auto-switches tool versions per project
- **Supply Chain**: Verified packages via extrepo

### Adding Tools

Edit [`src/wagov_devcontainer/spec.py`](src/wagov_devcontainer/spec.py) and add to the appropriate mapping:

```python
MISE_TOOLS = {
    # Simple: tool name -> pinned to "latest"
    "pipx:your-tool": "latest",  # or npm:, cargo:, github:user/repo

    # Complex: use structured values for inline TOML tables
    "pipx:tool": {"version": "latest", "extras": "extra", "uvx_args": "--with dep"},
}
```

`MISE_SETTINGS` is also structured Python data, and `MISE_TOML` is rendered from it.

For provisioning behaviour, edit [`src/wagov_devcontainer/deploy.py`](src/wagov_devcontainer/deploy.py). Then rebuild: `just build`

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidance.

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
just lint         # Format and lint Python sources
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
| Tool missing | Check `src/wagov_devcontainer/spec.py` |
| Build fails | Run `just clean` then `just build` |
| Docker permission errors | Rebuild the devcontainer so the `docker-outside-of-docker` feature can refresh socket access. For direct `docker run`, pass `--group-add $(stat -c '%g' /var/run/docker.sock)`. |
| mise issues | Run `mise doctor` inside container |

## Contributing

1. Fork and clone the repo
2. Make changes to `src/wagov_devcontainer/`, `Dockerfile`, or docs
3. Test: `just build && just test && just dev`
4. Submit PR with test results

**What to contribute:**
- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance optimisations

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidance and project philosophy.
