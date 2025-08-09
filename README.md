# Modern Cloud Native Devcontainer

A production-ready development container for cloud-native and infrastructure development, built with modern practices and optimized for performance.

## 🏗️ Architecture

**Base**: [`ghcr.io/astral-sh/uv:bookworm`](https://github.com/astral-sh/uv) - Debian Bookworm with UV and build essentials  
**Docker**: Official Docker CE with manual Docker-in-Docker setup  
**Package Management**: Hybrid approach - official Debian packages + mise for specialized tools  
**Build System**: Modern Docker BuildKit with optimized caching

## 🚀 Quick Start

### Use the Published Image
```bash
# Open in VS Code Dev Containers
# 1. Specifiy ghcr.io/wagov-dtt/devcontainer-base:latest as your base image
# 2. Open in VS Code 
# 3. Cmd/Ctrl+Shift+P → "Dev Containers: Reopen in Container"

# Or use directly with Docker
docker run -it --privileged \
  --mount source=dind-var-lib-docker,target=/var/lib/docker,type=volume \
  ghcr.io/wagov-dtt/devcontainer-base:latest
```

### For Image Development
```bash
# Core workflow (works locally or in Codespaces)
just test           # Build and test Docker-in-Docker
just dev            # Interactive development
just publish        # Build + publish + sign (requires GITHUB_TOKEN)
```

### Use as Template
1. **GitHub**: Use this template - gets you a ready-to-use devcontainer
2. **Codespaces**: Works immediately with the published image
3. **Local**: Customize [`devcontainer.json`](.devcontainer/devcontainer.json) to point to your own image

## 📦 Included Tools

### System Packages (Debian)

The container includes [Docker CE](https://docs.docker.com/) with BuildKit for container operations, plus official cloud CLIs: [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/), [Google Cloud CLI](https://cloud.google.com/sdk/gcloud), and [GitHub CLI](https://cli.github.com/). Development tools include [mise](https://mise.jdx.dev/) for tool management, [ddev](https://ddev.readthedocs.io/) for local environments, and utilities like [neovim](https://neovim.io/), [fzf](https://github.com/junegunn/fzf), [ripgrep](https://github.com/BurntSushi/ripgrep), and [btop](https://github.com/aristocratos/btop).

### Cloud & Infrastructure Tools

Infrastructure as code tools include [Terraform](https://www.terraform.io/) for declarative provisioning across multiple clouds, [AWS SAM](https://aws.amazon.com/serverless/sam/) for serverless application modeling, and [AWS CLI](https://aws.amazon.com/cli/) for imperative AWS operations. Kubernetes tooling includes [kubectl](https://kubernetes.io/docs/tasks/tools/), [Helm](https://helm.sh/) for templated deployments, [k9s](https://k9scli.io/) for cluster navigation, [k3d](https://k3d.io/) for local development clusters, and [Kustomize](https://kustomize.io/) for overlay-based configuration.

### Development Environment

Language runtimes include [Go](https://golang.org/), [Node.js](https://nodejs.org/) with [pnpm](https://pnpm.io/) for fast package management, and [Python](https://www.python.org/). Build tools centre around [just](https://just.systems/) for task automation and [yq](https://mikefarah.gitbook.io/yq/) for YAML processing. Security scanning uses [Trivy](https://trivy.dev/) for vulnerabilities, [Cosign](https://sigstore.dev/) for container signing, and [Vault](https://www.vaultproject.io/) for secret management.

### Productivity Tools

Terminal productivity includes [Zellij](https://zellij.dev/) for workspace management, [LazyGit](https://github.com/jesseduffield/lazygit) for Git operations, and [starship](https://starship.rs/) for shell prompts. Documentation and testing tools include [mdbook](https://rust-lang.github.io/mdBook/) for docs, [D2](https://d2lang.com/) for diagrams, [Hurl](https://hurl.dev/) for HTTP testing, [HTTPie](https://httpie.io/) for API calls, and [Lychee](https://lychee.cli.rs/) for link checking. Backup tools include [Restic](https://restic.net/) and [Rustic](https://rustic.cli.rs/).

## 🔧 Configuration

### Commands
```bash
# Development
just build           # Build test image locally
just test            # Test Docker-in-Docker functionality
just dev             # Interactive development shell (build + test + shell)
just scan            # Security scan with Trivy
just clean           # Clean up images and volumes

# Publishing (maintainers)
just publish         # Build + push + sign with cosign
just shell           # Run published image interactively
```

### Customization

**Add/remove tools**: Edit [`mise.toml`](mise.toml)
```toml
[tools]
your-tool = "latest"
```

**Custom packages**: Add to [`Dockerfile`](.devcontainer/Dockerfile) apt install section

**VS Code settings**: Add to [`devcontainer.json`](.devcontainer/devcontainer.json) customizations

## 🏭 Production Features

### Modern Docker Practices
- **BuildKit**: Advanced build features and caching
- **Multi-stage**: Optimized layer caching  
- **Secrets**: Secure GITHUB_TOKEN handling
- **Mounts**: Persistent cache mounts for package managers

### Security & Compliance
- **Official packages**: Debian repositories where available
- **Signed packages**: GPG verification for all external repos
- **Trivy scanning**: Automated vulnerability detection
- **Minimal attack surface**: No unnecessary services

### Performance Optimizations
- **Cache mounts**: apt, mise, and user data persistence
- **Volume persistence**: Docker-in-Docker storage optimization  
- **Parallel installs**: Concurrent tool installation
- **Smart retries**: Resilient network operations

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
- Infrastructure as Code (Terraform)  
- Container orchestration (Kubernetes)
- Serverless applications (AWS SAM)

### DevOps & SRE  
- Container builds and testing
- Security scanning (Trivy, Cosign)
- Backup solutions (Restic, Rustic)
- Monitoring and debugging tools

### Full-Stack Development
- Multiple runtime support (Go, Node.js, Python)
- Modern package managers (pnpm, uv)
- Documentation tools (mdbook, D2)
- API testing (Hurl, HTTPie)

## 🤝 Contributing

1. **Issues**: Report bugs or request features
2. **Pull Requests**: Improve tools, documentation, or performance  
3. **Testing**: Verify compatibility across environments
4. **Documentation**: Help others understand and use the project

### Development Workflow
```bash
# Make changes to Dockerfile or mise.toml
just dev          # Test changes interactively
just scan         # Security scan
# Submit PR with test results
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Debian](https://www.debian.org/) - Stable base operating system
- [buildpack-deps](https://github.com/docker-library/buildpack-deps) - Build dependencies foundation
- [mise](https://mise.jdx.dev/) - Polyglot tool version manager
- [UV](https://github.com/astral-sh/uv) - Ultra-fast Python tooling  
- [just](https://just.systems/) - Command runner
- [Devcontainers](https://containers.dev/) - Development container specification
