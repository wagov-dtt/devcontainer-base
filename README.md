# Modern Cloud Native Devcontainer

A production-ready development container for cloud-native and infrastructure development, built with modern practices and optimised for performance.

## Architecture

**Base**: [`debian:stable-backports`](https://github.com/debuerreotype/docker-debian-artifacts) - Debian 13 Trixie stable + backports  
**Docker**: Official Docker CE with manual Docker-in-Docker setup  
**Package Management**: Hybrid approach - official Debian packages + mise for specialized tools  
**Build System**: Modern Docker BuildKit with docker bake and optimised caching  
**Automation**: Pyinfra handles repository setup and package installation during container build

## 🚀 Quick Start

### Use as VS Code Devcontainer
Create a `.devcontainer/devcontainer.json` with the following configuration:
```json
{
	"name": "wagov-dtt devcontainer-base",
	"image": "ghcr.io/wagov-dtt/devcontainer-base",
	"privileged": true,
	"runArgs": [
		"--cgroupns=host"
	],
	"mounts": [
		"source=dind-var-lib-docker,target=/var/lib/docker,type=volume"
	],
	"remoteUser": "vscode"
}
```

**Required settings explained:**
- `"privileged": true` - Enables Docker-in-Docker functionality
- `"--cgroupns=host"` - **Required** for proper container networking and k3d/minikube cluster functionality
- `"mounts": [...]` - Persists Docker data across container rebuilds
- `"remoteUser": "vscode"` - Sets proper user permissions for VS Code integration

Then open in VS Code: Cmd/Ctrl+Shift+P → "Dev Containers: Reopen in Container"

### Install on existing Debian system
```bash
# Install devcontainer base tools on existing Debian system
curl -sSL https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/install.sh | sh

# Or run the pyinfra script directly if pipx or uv already installed
pipx run https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py
uv run https://raw.githubusercontent.com/wagov-dtt/devcontainer-base/main/build.py
```

### Use directly with Docker
```bash
# Basic usage
docker run -it --privileged --cgroupns=host \
  --mount source=dind-var-lib-docker,target=/var/lib/docker,type=volume \
  ghcr.io/wagov-dtt/devcontainer-base:latest

# Mount local development folder
docker run -it --privileged --cgroupns=host \
  --mount source=dind-var-lib-docker,target=/var/lib/docker,type=volume \
  --mount type=bind,source=/path/to/your/projects,target=/workspaces \
  ghcr.io/wagov-dtt/devcontainer-base:latest
```

**Project switching**: Mount your local dev folder to `/workspaces` - mise automatically switches tool versions based on each project's mise configuration.

### For Image Development
```bash
# Core workflow (works locally or in Codespaces)
just build          # Build test image locally with docker bake
just test           # Build and test Docker-in-Docker
just dev            # Interactive development shell
just publish        # Multi-platform build + publish + sign with provenance (requires GITHUB_TOKEN)
```

### Use as Template
1. **GitHub**: Click "Use this template" to create your own repository
2. **Codespaces**: Works immediately - click "Code" → "Create codespace"
3. **Local**: Clone and customize [`devcontainer.json`](.devcontainer/devcontainer.json) as needed

### Use in CI/CD

Use [devcontainers/ci](https://github.com/devcontainers/ci) to run `mise` tasks and `just` recipes in your devcontainer for guaranteed environment consistency:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActions
    aws-region: ap-southeast-2

- name: Run tests in devcontainer
  uses: devcontainers/ci@v0.3
  with:
    imageName: local/devcontainer
    push: never
    inheritEnv: true
    runCmd: |
      just test
      mise run lint
```

**Alternative**: Use [mise GitHub Action](https://github.com/jdx/mise-action) for simple tool management without containers

## 📦 Included Tools

**Languages**: Go, Node.js, Python, Rust toolchain  
**Cloud**: AWS/Azure/GCP CLIs, Terraform, Kubernetes (kubectl, k9s, k3d), Docker  
**Development**: Git, just, mise, direnv, starship, zellij, LazyGit, neovim, envsubst  
**Security**: Trivy, Semgrep, cosign, slsa-verifier  

> **Complete list**: See [`build.py`](build.py) for all tools and versions  
> **Learning**: Use `tldr <command>` for quick examples of any CLI tool

## 🔧 Configuration

### Commands
```bash
# Development
just build           # Build test image locally with docker bake
just test            # Test Docker-in-Docker functionality
just dev             # Interactive development shell (build + test + shell)
just scan            # Security scan with Trivy
just clean           # Clean up images and volumes

# Publishing (maintainers)  
just publish         # Multi-platform build + push + sign with provenance
just shell           # Run published image interactively
```

### Customization

**Tools**: Edit [`build.py`](build.py) MISE_TOOLS and APT_PACKAGES sections  
**Versions**: Pin specific versions in [`build.py`](build.py) MISE_TOML  
**VS Code**: Customize [`devcontainer.json`](.devcontainer/devcontainer.json)  
**Build**: Modify [`docker-bake.hcl`](docker-bake.hcl) for advanced options

## Features

**Security**: SBOM generation, signed packages, Trivy scanning, minimal attack surface  
**Performance**: Multi-platform native builds, persistent caching, optimised layers  
**Docker-in-Docker**: Privileged mode with volume persistence and automatic startup  
**Repository Management**: Uses extrepo for secure standardised repos (Docker, Kubernetes, etc.)

## Use Cases

**Cloud**: Multi-cloud CLIs, Terraform, Kubernetes, serverless development  
**DevOps**: Container builds, security scanning, backup solutions, monitoring  
**Development**: Go/Node.js/Python, package management, documentation, API testing

## Contributing

1. **Issues**: Report bugs or request features
2. **Pull Requests**: Improve tools, documentation, or performance  
3. **Testing**: Verify compatibility across environments
4. **Documentation**: Help others understand and use the project

### Development Workflow
```bash
# Make changes to build.py, docker-bake.hcl, or Dockerfile
just build        # Build test image locally with docker bake
just test         # Test Docker-in-Docker functionality
just dev          # Interactive development shell
just scan         # Security scan with Trivy
# Submit PR with test results
```

### Troubleshooting
- **Docker issues**: Ensure `privileged: true` and volume mount are configured
- **Tool conflicts**: Run `mise install` to refresh tool installations
- **Build cache**: Use `just clean` to reset Docker build cache if needed

## Acknowledgments

- [Debian](https://www.debian.org/) - Stable base operating system
- [mise](https://mise.jdx.dev/) - Polyglot tool version manager
- [just](https://just.systems/) - Command runner
- [Devcontainers](https://containers.dev/) - Development container specification
- [Docker](https://www.docker.com/) - Container platform and BuildKit
