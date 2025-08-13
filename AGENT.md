# AGENT.md - Cloud Native Devcontainer

## Build/Test Commands
- `just build` - Build test image locally with docker bake
- `just test` - Test Docker-in-Docker functionality
- `just dev` - Interactive development shell (build + test + shell)
- `just scan` - Security scan with Trivy
- `just clean` - Clean up images and volumes

## Publishing Commands (Maintainers)
- `just publish` - Multi-platform build + push + sign with cosign (full pipeline) 
- `just shell` - Run published image interactively

## Tool Management
- `mise install` - Install tools from mise.toml
- `mise outdated` - Check for tool updates
- `mise upgrade` - Upgrade all tools

## Architecture & Structure
- **Base Image**: `debian:stable-backports` (Debian 13 Trixie stable + backports)
- **Package Management**: Hybrid approach - Debian packages for official tools, mise for specialized tools
- **Docker**: Official Docker CE with manual Docker-in-Docker setup (not Microsoft feature)
- **Build System**: Modern Docker BuildKit with docker bake and optimised caching
- **Files**:
  - `Dockerfile`: Container build definition with multi-stage optimisation
  - `.devcontainer/`: Minimal devcontainer configuration (devcontainer.json)
  - `docker-bake.hcl`: Declarative build configuration with HCL functions, SBOM & provenance
  - `mise.toml`: Tool definitions organised by category (matches README structure)
  - `justfile`: Modern task runner with elegant commands
  - `mise.lock`: Lock file for reproducible tool installations

## Modern Improvements Made
- **Simplified devcontainer.json**: Minimal config matching Microsoft defaults
- **Official packages**: Azure CLI, Google Cloud CLI, GitHub CLI via Debian repos
- **Clean base**: debian:stable-backports with only needed core packages
- **Task automation**: `just` commands for all development workflows
- **Performance**: BuildKit caching, volume mounts, concurrent installs
- **Security**: Official packages where available, GPG verification

## Tool Installation Sources
- **Debian packages**: See `Dockerfile` for complete package list and repository setup
- **mise tools**: See `mise.toml` for tool definitions organised by category

## Code Style & Conventions
- **Modern Docker**: Docker bake with HCL functions, BuildKit features, cache mounts, multi-stage optimisation
- **Supply chain security**: SBOM and enhanced provenance (`mode=max`) for all builds
- **Variable handling**: Use environment variables for bake variables, `--set` for target overrides
- **Language**: Use Australian English spelling (organise vs organize, colour vs color, etc.)
- **Hybrid package management**: Official repos where available, mise for rest
- **Task automation**: Use `just` commands instead of raw docker/devcontainer commands
- **Security-first**: Official packages, signed repos, minimal attack surface
- **Performance-oriented**: Optimised caching, persistent volumes, parallel installs
- **Developer experience**: Simple commands, clear documentation, fast builds
