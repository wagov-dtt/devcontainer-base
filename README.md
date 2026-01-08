# Cloud Native Devcontainer

Production-ready development container with modern tooling for cloud-native and infrastructure development.

## What's Inside

**Languages**: Go, Node.js, Python, Rust  
**Cloud**: AWS, Azure, GCP CLIs, Terraform, Kubernetes tools (kubectl, k9s, k3d)  
**AI Tools**: goose (AI coding agent), litellm (LLM proxy with AWS Bedrock support)  
**Development**: Docker-in-Docker, git, just, mise, direnv, starship, zellij, neovim  
**Security**: Trivy, Semgrep, cosign, SLSA verification

> 💡 **Complete list**: See [`build.py`](build.py) - all tools defined in one place

## 🚀 Quick Start

### VS Code Devcontainer (Recommended)

Create `.devcontainer/devcontainer.json`:
```json
{
  "name": "My Project",
  "image": "ghcr.io/wagov-dtt/devcontainer-base",
  "privileged": true,
  "runArgs": ["--cgroupns=host"],
  "mounts": ["source=dind-var-lib-docker,target=/var/lib/docker,type=volume"],
  "remoteUser": "vscode"
}
```

Open in VS Code: **Cmd/Ctrl+Shift+P** → "Dev Containers: Reopen in Container"

<details>
<summary>Why these settings?</summary>

- `privileged: true` - Enables Docker-in-Docker
- `--cgroupns=host` - Required for k3d/minikube networking
- Docker volume - Persists data across rebuilds
- `remoteUser: vscode` - Correct user permissions
</details>

### Docker CLI

```bash
# Basic usage
docker run -it --privileged --cgroupns=host \
  -v dind-var-lib-docker:/var/lib/docker \
  ghcr.io/wagov-dtt/devcontainer-base

# With your projects mounted
docker run -it --privileged --cgroupns=host \
  -v dind-var-lib-docker:/var/lib/docker \
  -v ~/projects:/workspaces \
  ghcr.io/wagov-dtt/devcontainer-base
```

### Install on Existing System

```bash
# Debian/Ubuntu only
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh

# Or with pipx/uv already installed
pipx run https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py
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

## 📚 How It Works

### Architecture

- **Base**: Debian 13 (Trixie) stable + backports
- **Package Management**: APT for system tools, mise for development tools
- **Build**: Pyinfra script installs everything during Docker build
- **Docker-in-Docker**: Automatic startup, volume persistence

### Key Features

- **🔒 Security**: SBOM, signed images, Trivy scanning
- **⚡ Performance**: Multi-platform builds, layer caching
- **🔧 Flexibility**: mise auto-switches tool versions per project
- **📦 Supply Chain**: Verified packages via extrepo

### Adding Tools

Edit [`build.py`](build.py) and add to the appropriate list:

```python
# Simple tool
MISE_TOOLS = (
    + ["pipx:your-tool"]  # or npm:, cargo:, ubi:user/repo
)

# Complex tool with config
MISE_TOOLS = (
    + [("pipx:tool", '{ version = "latest", extras = "extra", uvx_args = "--with dep" }')]
)
```

Then rebuild: `just build`

See [AGENTS.md](AGENTS.md) for detailed guidance.

## 🤖 AI Development

This container includes AI coding tools:

- **goose** - AI coding agent from Block ([docs](https://block.github.io/goose))
- **litellm** - Unified LLM proxy (OpenAI, Anthropic, AWS Bedrock, etc.)

```bash
# Start using goose
goose session start

# Or use litellm proxy
litellm --model gpt-4
```

boto3 is automatically included in litellm for AWS Bedrock authentication.

## 🔧 Development Commands

```bash
just              # List all commands
just build        # Build test image
just test         # Test Docker-in-Docker
just dev          # Interactive shell
just scan         # Security scan
just clean        # Clean up
```

**For maintainers:**
```bash
just publish      # Multi-platform build + sign
just shell        # Run published image
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker won't start | Check `privileged: true` and `--cgroupns=host` |
| Tool missing | Check `build.py` MISE_TOOLS or APT_PACKAGES |
| Build fails | Run `just clean` then `just build` |
| Permission errors | User should be in docker group (automatic) |
| mise issues | Run `mise doctor` inside container |

## 🤝 Contributing

1. Fork and clone the repo
2. Make changes to `build.py`, `Dockerfile`, or docs
3. Test: `just build && just test && just dev`
4. Submit PR with test results

**What to contribute:**
- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance optimisations

See [AGENTS.md](AGENTS.md) for AI agent guidance and grug-brain philosophy.
