# Cloud Native Devcontainer

Production-ready development container with modern tooling for cloud-native and infrastructure development.

## What's Inside

**Languages**: [Go](https://go.dev), [Node.js](https://nodejs.org), [Python](https://python.org), [Rust](https://rust-lang.org) (via [cargo-binstall](https://github.com/cargo-bins/cargo-binstall)), [uv](https://github.com/astral-sh/uv), [pnpm](https://pnpm.io)  
**Cloud**: [AWS CLI](https://aws.amazon.com/cli/), [Terraform](https://terraform.io), Kubernetes ([kubectl](https://kubernetes.io/docs/reference/kubectl/), [k9s](https://k9scli.io), [k3d](https://k3d.io), [helm](https://helm.sh), [kustomize](https://kustomize.io))  
**Development**: Docker-from-Docker, [git](https://git-scm.com), [just](https://just.systems), [mise](https://mise.jdx.dev), [direnv](https://direnv.net), [starship](https://starship.rs), [zellij](https://zellij.dev), [neovim](https://neovim.io), [lazygit](https://github.com/jesseduffield/lazygit)  
**Security**: [Semgrep](https://semgrep.dev), [cosign](https://github.com/sigstore/cosign), [SLSA verifier](https://github.com/slsa-framework/slsa-verifier), [lychee](https://lychee.cli.rs) (link checker)  
**Utilities**: [ripgrep](https://github.com/BurntSushi/ripgrep), [fzf](https://github.com/junegunn/fzf), [jq](https://jqlang.github.io/jq/), [yq](https://mikefarah.gitbook.io/yq), [httpie](https://httpie.io), [hurl](https://hurl.dev), [btop](https://github.com/aristocratos/btop), [restic](https://restic.net), [rclone](https://rclone.org)

> **Complete list**: See [`src/wagov_devcontainer/spec.py`](src/wagov_devcontainer/spec.py) and [`src/wagov_devcontainer/deploy.py`](src/wagov_devcontainer/deploy.py)

## Quick Start

### VS Code Devcontainer (Recommended)

Create `.devcontainer/devcontainer.json`:
```json
{
  "name": "My Project",
  "image": "ghcr.io/wagov-dtt/devcontainer-base",
  "mounts": [
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ],
  "onCreateCommand": "docker-init.sh",
  "remoteEnv": {
    "LOCAL_WORKSPACE_FOLDER": "${localWorkspaceFolder}",
    "DOCKER_API_VERSION": "1.43"
  },
  "remoteUser": "vscode"
}
```

Open in VS Code: **Cmd/Ctrl+Shift+P** → "Dev Containers: Reopen in Container"

<details>
<summary>Why these settings?</summary>

- Docker socket bind mount - Enables Docker via host socket (no privileged mode needed, Docker CLI pre-installed via extrepo)
- `onCreateCommand` - Runs baked-in `docker-init.sh` which fixes socket permissions
- `DOCKER_API_VERSION` - Caps Docker client API version for compatibility with older daemons (set to 1.43 for broad compatibility)
- `LOCAL_WORKSPACE_FOLDER` - Enables bind mounts from inside the container using host paths
- `remoteUser: vscode` - Correct user permissions
</details>

### Docker CLI

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

```bash
# Preferred: run the published package directly
uvx wagov-devcontainer

# Or with pipx
pipx run --spec wagov-devcontainer wagov-devcontainer

# Repo helper script for Debian/Ubuntu
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh
```

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
- **Docker-from-Docker**: Host socket bind mount (Docker CLI pre-installed via extrepo, no privileged mode needed)

### Tool Sources

Tools are installed from two sources, preferring APT when available:

1. **APT via [extrepo](https://wiki.debian.org/ExtRepo)** (preferred) - Signed packages from official repos
   - Docker, GitHub CLI, Terraform, kubectl, mise
2. **[mise](https://mise.jdx.dev)** - Cross-platform tools not in APT, or needing version flexibility
   - Languages (Go, Node, Python), k9s, starship

### Key Features

- **Security**: SBOM, signed images, Semgrep in-container
- **Performance**: Multi-platform builds (amd64/arm64), layer caching
- **Flexibility**: mise auto-switches tool versions per project
- **Supply Chain**: Verified packages via extrepo

### Adding Tools

Edit [`src/wagov_devcontainer/spec.py`](src/wagov_devcontainer/spec.py) and add to the appropriate list:

```python
MISE_TOOLS = (
    # Simple: just the tool name (defaults to latest)
    + ["pipx:your-tool"]  # or npm:, cargo:, github:user/repo

    # Complex: tuple with TOML config string
    + [("pipx:tool", '{ version = "latest", extras = "extra", uvx_args = "--with dep" }')]
)
```

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
just test         # Test Docker-from-Docker
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
| Docker not working | Ensure Docker socket is available on the host |
| Tool missing | Check `src/wagov_devcontainer/spec.py` |
| Build fails | Run `just clean` then `just build` |
| Permission errors | User should be in docker group (automatic) |
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
