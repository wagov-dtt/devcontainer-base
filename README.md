# Modern Cloud Native Devcontainer

A production-ready development container for cloud-native and infrastructure development, built with modern practices and optimised for performance.

## 🏗️ Architecture

**Base**: [`debian:stable-backports`](https://github.com/debuerreotype/docker-debian-artifacts) - Debian 13 Trixie stable + backports  
**Docker**: Official Docker CE with manual Docker-in-Docker setup  
**Package Management**: Hybrid approach - official Debian packages + mise for specialized tools  
**Build System**: Modern Docker BuildKit with docker bake and optimised caching

## 🚀 Quick Start

### Use as VS Code Devcontainer
Create a `.devcontainer/devcontainer.json` with the following configuration:
```json
{
  "name": "your-project-name",
  "image": "ghcr.io/wagov-dtt/devcontainer-base",
  "privileged": true,
  "mounts": ["source=dind-var-lib-docker,target=/var/lib/docker,type=volume"],
  "remoteUser": "vscode"
}
```

**Required settings explained:**
- `"privileged": true` - Enables Docker-in-Docker functionality
- `"mounts": [...]` - Persists Docker data across container rebuilds
- `"remoteUser": "vscode"` - Sets proper user permissions for VS Code integration

Then open in VS Code: Cmd/Ctrl+Shift+P → "Dev Containers: Reopen in Container"

### Use directly with Docker
```bash
docker run -it --privileged \
  --mount source=dind-var-lib-docker,target=/var/lib/docker,type=volume \
  ghcr.io/wagov-dtt/devcontainer-base:latest
```

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

## 📦 Included Tools

This container uses a hybrid approach: essential tools via Debian packages, specialized tools via [mise](https://mise.jdx.dev/).

### System & Core Tools (Debian packages)
- **Docker**: [Docker CE](https://docs.docker.com/) with BuildKit, compose, and buildx plugins
- **Cloud CLIs**: [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/), [Google Cloud CLI](https://cloud.google.com/sdk/gcloud), [GitHub CLI](https://cli.github.com/)
- **Infrastructure**: [Terraform](https://www.terraform.io/) with [TFLint](https://github.com/terraform-linters/tflint) & [terraform-docs](https://terraform-docs.io/), [Helm](https://helm.sh/), [ddev](https://ddev.readthedocs.io/)
- **Development**: [neovim](https://neovim.io/), [fzf](https://github.com/junegunn/fzf), [ripgrep](https://github.com/BurntSushi/ripgrep), [btop](https://github.com/aristocratos/btop), [htop](https://htop.dev/)
- **Build tools**: build-essential, ca-certificates, openssh-client
- **System utilities**: less, [jq](https://jqlang.github.io/jq/), unzip, zip, file, [rsync](https://rsync.samba.org/), bash-completion
- **Network tools**: iputils-ping, dnsutils, net-tools, procps, lsof  
- **File management**: [restic](https://restic.net/), [rclone](https://rclone.org/), ugrep

### Language Runtimes & Development (mise)
- **Languages**: [Go](https://golang.org/), [Node.js](https://nodejs.org/), [Python](https://www.python.org/)
- **Package Managers**: [pnpm](https://pnpm.io/), [uv](https://github.com/astral-sh/uv), [pipx](https://pypa.github.io/pipx/)
- **Build Tools**: [just](https://just.systems/), [yq](https://mikefarah.gitbook.io/yq/)

### Cloud & Kubernetes (mise)
- **AWS**: [AWS CLI](https://aws.amazon.com/cli/), [AWS SAM](https://aws.amazon.com/serverless/sam/)
- **Kubernetes**: [kubectl](https://kubernetes.io/docs/tasks/tools/), [k9s](https://k9scli.io/), [k3d](https://k3d.io/), [kustomize](https://kustomize.io/)
- **Infrastructure**: [TFLint](https://github.com/terraform-linters/tflint), [terraform-docs](https://terraform-docs.io/)
- **Security**: [Trivy](https://trivy.dev/), [Vault](https://www.vaultproject.io/)

### Productivity & Terminal (mise)
- **Terminal**: [Zellij](https://zellij.dev/), [starship](https://starship.rs/), [zoxide](https://github.com/ajeetdsouza/zoxide), [eza](https://eza.rocks/), [direnv](https://direnv.net/), [tldr](https://tldr.sh/)
- **Git**: [LazyGit](https://github.com/jesseduffield/lazygit)
- **Documentation**: [mdbook](https://rust-lang.github.io/mdBook/), [Lychee](https://lychee.cli.rs/), [rumdl](https://github.com/rvben/rumdl)
- **Testing**: [Hurl](https://hurl.dev/), [HTTPie](https://httpie.io/)
- **Package Managers**: [@devcontainers/cli](https://github.com/devcontainers/cli), [cargo-binstall](https://github.com/cargo-bins/cargo-binstall)

> **Current tools**: See [`mise.toml`](mise.toml) and [`Dockerfile`](Dockerfile) for complete, up-to-date lists.
> 
> **Learning CLI tools**: Use `tldr <command>` to get practical examples for any CLI tool - much faster than reading full man pages.

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

**Add/remove tools**: Edit [`mise.toml`](mise.toml)
```toml
[tools]
your-tool = "latest"
```

**Custom packages**: Add to [`Dockerfile`](Dockerfile) APT install section

**Build configuration**: Modify [`docker-bake.hcl`](docker-bake.hcl) for advanced build options

**VS Code settings**: Add to [`devcontainer.json`](.devcontainer/devcontainer.json) customizations

**Environment variables**: Set in [`devcontainer.json`](.devcontainer/devcontainer.json) or during runtime

## 🏭 Production Features

### Modern Docker Practices
- **Docker Bake**: Declarative multi-platform builds with HCL functions and native manifest creation
- **Supply Chain Security**: Comprehensive SBOM generation and enhanced provenance attestations (`mode=max`)
- **BuildKit**: Advanced build features with squashed layers and zstd compression
- **Secrets**: Secure GITHUB_TOKEN handling for private repository access
- **Cache mounts**: Persistent cache for APT packages and mise downloads

### Security & Compliance
- **Supply chain attestations**: Automated SBOM and detailed provenance generation for every build
- **Official packages**: Debian repositories where available
- **Signed packages**: GPG verification for all external repos
- **Trivy scanning**: Automated vulnerability detection
- **Minimal attack surface**: No unnecessary services

### Performance Optimisations
- **Native builds**: AMD64/ARM64 compile on matching hardware, no QEMU emulation
- **Cache mounts**: APT packages and mise downloads persist across builds
- **Architecture-specific caching**: Separate cache scopes prevent conflicts
- **Single APT transaction**: Merged system upgrade and package installation
- **Volume persistence**: Docker-in-Docker storage optimisation  
- **Smart retries**: Resilient network operations for mise tool installation

## 🔐 Docker-in-Docker

### Features
- **Privileged mode**: Full Docker daemon access
- **Volume persistence**: Shared Docker storage across rebuilds
- **Automatic startup**: Docker daemon starts with container
- **Health checks**: Ensures Docker is ready before use

### Security Considerations
- Uses official Docker CE
- No unnecessary network exposure
- User-scoped permissions via docker group

## 🎯 Use Cases

### Cloud Development
- Multi-cloud CLI tools (AWS, Azure, GCP)
- Infrastructure as Code (Terraform with linting & documentation)  
- Container orchestration (Kubernetes)
- Serverless applications (AWS SAM)

### DevOps & SRE  
- Container builds and testing
- Security scanning (Trivy) with automated provenance
- Backup solutions (Restic, rclone)
- Monitoring and debugging tools

### Full-Stack Development
- Multiple runtime support (Go, Node.js, Python)
- Modern package managers (pnpm, uv)
- Documentation tools (mdbook, Lychee)
- API testing (Hurl, HTTPie)

## 🤝 Contributing

1. **Issues**: Report bugs or request features
2. **Pull Requests**: Improve tools, documentation, or performance  
3. **Testing**: Verify compatibility across environments
4. **Documentation**: Help others understand and use the project

### Development Workflow
```bash
# Make changes to Dockerfile, mise.toml, or docker-bake.hcl
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

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Debian](https://www.debian.org/) - Stable base operating system
- [mise](https://mise.jdx.dev/) - Polyglot tool version manager
- [just](https://just.systems/) - Command runner
- [Devcontainers](https://containers.dev/) - Development container specification
- [Docker](https://www.docker.com/) - Container platform and BuildKit
