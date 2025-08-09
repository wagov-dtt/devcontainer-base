# AGENT.md - Cloud Native Devcontainer

## Build/Test Commands
- `just build` - Build test image locally
- `just test` - Test Docker-in-Docker functionality
- `just dev` - Interactive development shell (build + test + shell)
- `just scan` - Security scan with Trivy
- `just clean` - Clean up images and volumes

## Publishing Commands (Maintainers)
- `just publish` - Build + push + sign with cosign (full pipeline) 
- `just shell` - Run published image interactively

## Tool Management
- `mise install` - Install tools from mise.toml
- `mise outdated` - Check for tool updates
- `mise upgrade` - Upgrade all tools

## Architecture & Structure
- **Base Image**: `ghcr.io/astral-sh/uv:debian` (Debian Bookworm + UV + build tools)
- **Package Management**: Hybrid approach - Debian packages for official tools, mise for specialized tools
- **Docker**: Official Docker CE with manual Docker-in-Docker setup (not Microsoft feature)
- **Build System**: Modern Docker BuildKit with optimized caching
- **Files**:
  - `.devcontainer/`: Minimal Docker configuration (Dockerfile, devcontainer.json)
  - `mise.toml`: Tool definitions organized by category
  - `justfile`: Modern task runner with elegant commands
  - `mise.lock`: Lock file for reproducible tool installations

## Modern Improvements Made
- **Simplified devcontainer.json**: Minimal config matching Microsoft defaults
- **Official packages**: Azure CLI, Google Cloud CLI, GitHub CLI via Debian repos
- **Better base**: UV image provides modern Python tooling + build essentials  
- **Task automation**: `just` commands for all development workflows
- **Performance**: BuildKit caching, volume mounts, concurrent installs
- **Security**: Official packages where available, GPG verification

## Tool Installation Sources
- **Debian packages**: Docker CE, Azure CLI, Google Cloud CLI, GitHub CLI, mise, ddev, bash-completion, vim, neovim, fzf, ripgrep, ugrep, btop, tree, htop
- **mise tools**: AWS CLI, AWS SAM, Go, Node.js, Python, pnpm, Terraform, Trivy, Cosign, Vault, just, yq, Hurl, Lychee, kubectl, Helm, k9s, k3d, Kustomize, mdbook, D2, Restic, Rustic, Zellij, LazyGit, cargo-binstall, @devcontainers/cli, HTTPie, rumdl, starship

## Code Style & Conventions
- **Modern Docker**: BuildKit features, cache mounts, multi-stage optimization
- **Hybrid package management**: Official repos where available, mise for rest
- **Task automation**: Use `just` commands instead of raw docker/devcontainer commands
- **Security-first**: Official packages, signed repos, minimal attack surface
- **Performance-oriented**: Optimized caching, persistent volumes, parallel installs
- **Developer experience**: Simple commands, clear documentation, fast builds
