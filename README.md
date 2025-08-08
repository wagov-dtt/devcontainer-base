# devcontainer-base

A comprehensive devcontainer template for cloud-native and infrastructure development. All tools are managed and installed using [mise](https://mise.jdx.dev/), a polyglot tool version manager that ensures reproducible, version-pinned development environments.

## Included Tools

### Cloud Platforms
- **[AWS CLI](https://aws.amazon.com/cli/)** - Command line interface for Amazon Web Services
- **[AWS SAM](https://aws.amazon.com/serverless/sam/)** - Serverless Application Model CLI for building and deploying serverless applications
- **[Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)** - Command line tools for Microsoft Azure (via pipx)
- **[Google Cloud SDK](https://cloud.google.com/sdk/gcloud)** - CLI tools and libraries for Google Cloud Platform
- **[GitHub CLI](https://cli.github.com/)** - Official command line tool for GitHub

### Kubernetes & Container Tools
- **[kubectl](https://kubernetes.io/docs/reference/kubectl/)** - Kubernetes command-line tool
- **[Helm](https://helm.sh/)** - Kubernetes package manager
- **[k9s](https://k9scli.io/)** - Terminal-based UI for Kubernetes clusters
- **[k3d](https://k3d.io/)** - Lightweight Kubernetes distribution in Docker
- **[Kustomize](https://kustomize.io/)** - Kubernetes configuration management tool

### Programming Languages & Runtimes
- **[Go](https://golang.org/)** - The Go programming language
- **[Node.js](https://nodejs.org/)** - JavaScript runtime
- **[Python](https://www.python.org/)** - Python programming language
- **[pnpm](https://pnpm.io/)** - Fast, disk space efficient package manager for Node.js
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package installer and resolver

### Infrastructure & Security
- **[Terraform](https://www.terraform.io/)** - Infrastructure as Code tool
- **[Trivy](https://trivy.dev/)** - Vulnerability scanner for containers and other artifacts
- **[Cosign](https://sigstore.dev/)** - Container signing and verification tool
- **[HashiCorp Vault](https://www.vaultproject.io/)** - Secrets management and data protection

### Development Tools
- **[just](https://just.systems/)** - Command runner and build tool
- **[jq](https://jqlang.github.io/jq/)** - Lightweight JSON processor
- **[yq](https://mikefarah.gitbook.io/yq/)** - YAML processor (jq for YAML)
- **[ripgrep (rg)](https://github.com/BurntSushi/ripgrep)** - Ultra-fast text search tool
- **[ugrep](https://ugrep.com/)** - Ultra-fast grep alternative with advanced features
- **[HTTPie](https://httpie.io/)** - Modern, user-friendly HTTP client for API testing (via pipx)
- **[Hurl](https://hurl.dev/)** - HTTP testing tool
- **[Lychee](https://lychee.rs/)** - Fast link checker
- **[rumdl](https://github.com/rvben/rumdl)** - High-performance Markdown linter and formatter written in Rust

### Documentation & Diagramming
- **[mdBook](https://rust-lang.github.io/mdBook/)** - Static site generator for documentation (via cargo)
- **[D2](https://d2lang.com/)** - Declarative diagramming language

### Backup & Recovery
- **[Restic](https://restic.net/)** - Fast, secure backup program
- **[Rustic](https://rustic.cli.rs/)** - Fast, encrypted, deduplicated backups powered by Rust

### Terminal & Productivity
- **[Zellij](https://zellij.dev/)** - Terminal workspace with batteries included
- **[DDEV](https://ddev.com/)** - Docker-based local development environment
- **[fzf](https://github.com/junegunn/fzf)** - Command-line fuzzy finder for enhanced productivity
- **[btop](https://github.com/aristocratos/btop)** - Modern resource monitor with improved visuals
- **[LazyGit](https://github.com/jesseduffield/lazygit)** - Terminal UI for git commands

### Package Managers & Installers
- **[cargo-binstall](https://github.com/cargo-bins/cargo-binstall)** - Fast Rust binary installer
- **[DevContainer CLI](https://github.com/devcontainers/cli)** - Reference implementation of the dev container specification

## mise - Tool Version Management

This project uses [mise](https://mise.jdx.dev/) (formerly rtx) as a polyglot tool version manager. mise provides:

- **Reproducible environments**: All tools are pinned to specific versions
- **Multiple backends**: Supports asdf plugins, cargo, npm, pipx, and direct downloads
- **Automatic activation**: Tools are available when you enter the project directory
- **Lockfile support**: `mise.lock` ensures exact version reproducibility

### Key Features in This Project

- **Latest versions**: All tools use `"latest"` to stay current with upstream releases
- **Multiple package sources**: 
  - Direct tool support (terraform, node, python)
  - cargo packages (mdbook via `cargo:mdbook`)
  - npm packages (devcontainer CLI via `npm:@devcontainers/cli`)
  - pipx packages (azure-cli via `pipx:azure-cli`)
  - GitHub releases (ddev via `github:ddev/ddev`)
  - HTTP downloads (ugrep with specific version pinning)

### Common mise Commands

```bash
# Install all tools defined in mise.toml
mise install

# List all installed tools and versions
mise list

# Update all tools to latest versions
mise upgrade

# Check for available updates
mise outdated

# Add a new tool
mise use tool@version

# Remove a tool
mise uninstall tool@version
```

## Setup
```bash
npm install -g @devcontainers/cli
curl https://mise.run/bash | sh
source ~/.bashrc
# Setup tools with `mise use` in the devcontainer-base subfolder
mise use just
# Build the image with tools included by dockerfile
devcontainer build --workspace-folder .
```

## Local Development
```bash
# Build locally (with optional GitHub token to avoid rate limits)
export GITHUB_TOKEN=your_token_here
devcontainer build --workspace-folder . --image-name devcontainer-base:local

# Test the container
docker run -it --rm --user vscode devcontainer-base:local bash

# Test tools are installed (copy/paste friendly)
docker run --rm --user vscode devcontainer-base:local bash -l -c 'mise list'
```

## Security Scanning

This project uses Trivy for vulnerability scanning with focused configuration:
- Only reports HIGH/CRITICAL severity vulnerabilities
- Scans all package types (OS packages, libraries, etc.)
- Includes secrets, misconfigurations, and vulnerabilities

### Managing .trivyignore

The `.trivyignore` file filters out OS-level vulnerabilities that aren't actionable in a devcontainer context. When updating:

1. **Review new vulnerabilities**: Check if they affect development tools vs base OS
2. **Document reasoning**: Add comments explaining why CVEs are ignored
3. **Periodic review**: Remove ignored CVEs when they're fixed in base images
4. **Test locally**: Run `trivy --scanners vuln --severity HIGH,CRITICAL image devcontainer-base:local` to verify filtering
