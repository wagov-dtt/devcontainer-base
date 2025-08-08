# AGENT.md - Development Container Base

## Build/Test/Lint Commands
- `devcontainer build --workspace-folder devcontainer-base` - Build the devcontainer image
- `devcontainer build --workspace-folder devcontainer-base --image-name devcontainer-base:local` - Build locally
- `trivy image devcontainer-base:local` - Security scan with Trivy
- `mise install` - Install all tools defined in mise.toml
- `mise use just` - Install just task runner
- CI/CD: GitHub Actions builds, scans with Trivy, signs with Cosign, pushes to ghcr.io/wagov-dtt/devcontainer-base

## Architecture & Structure
- **Root**: Repository contains README.md, LICENSE, and main devcontainer-base/ folder
- **devcontainer-base/**: Contains the actual devcontainer configuration
  - `.devcontainer/`: Docker configuration (Dockerfile, devcontainer.json)
  - `mise.toml`: Tool definitions and versions using mise package manager
  - `mise.lock`: Lock file for reproducible tool installations

## Project Purpose
This is a base devcontainer template for cloud-native and infrastructure development. It pre-installs essential tools including:
- Cloud CLIs: AWS, Azure (pipx), GCP
- Kubernetes: kubectl, helm, k9s, k3d, kustomize
- Languages: Go, Node.js, Python
- Infrastructure: Terraform, Trivy security scanner
- Utilities: jq, yq, just, zellij terminal multiplexer, ripgrep

## Code Style & Conventions
- Infrastructure-as-code focused repository
- Use mise for tool version management
- All tools pinned to "latest" version
- Docker best practices: non-root user (vscode), proper COPY ownership
- No application code - purely configuration and tooling setup
