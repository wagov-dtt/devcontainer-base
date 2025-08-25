# Cloud Native Devcontainer

Cloud native development container with modern tooling for operations & development teams.

## Setup Commands

- `mise install` - Install tools from mise.toml
- `just build` - Build test image locally with docker bake
- `just test` - Test Docker-in-Docker functionality
- `just dev` - Interactive development shell (build + test + shell)
- `pipx run pyinfra @local -y build.py` - Install devcontainer base via pyinfra (automated setup)

## Testing Instructions

- Run `just test` to test Docker-in-Docker functionality
- Run `just scan` for security scanning with Trivy
- All tests should pass before making changes
- Test the container build with `just build` after modifications

## Build Commands

- `just build` - Build test image locally with docker bake
- `just publish` - Multi-platform build + push + sign with cosign (maintainers only)
- `just clean` - Clean up images and volumes
- `just shell` - Run published image interactively

## Code Style

- **Language**: Use Australian English spelling (organise vs organize, colour vs color, etc.)
- **Modern Docker**: Docker bake with HCL functions, BuildKit features, cache mounts, multi-stage optimisation
- **Supply chain security**: SBOM and enhanced provenance (`mode=max`) for all builds
- **Variable handling**: Use environment variables for bake variables, `--set` for target overrides
- **Hybrid package management**: Official repos where available, mise for rest
- **Task automation**: Use `just` commands instead of raw docker/devcontainer commands

## Architecture

- **Base Image**: `debian:stable-backports` (Debian 13 Trixie stable + backports)
- **Package Management**: Hybrid approach - Debian packages for official tools, mise for specialised tools
- **Docker**: Official Docker CE with manual Docker-in-Docker setup
- **Build System**: Modern Docker BuildKit with docker bake and optimised caching
- **Automation**: Pyinfra (build.py) handles repository setup and package installation during container build

## Project Structure

- `Dockerfile` - Container build definition with multi-stage optimisation
- `.devcontainer/` - Minimal devcontainer configuration
- `docker-bake.hcl` - Declarative build configuration with HCL functions, SBOM & provenance
- `mise.toml` - Tool definitions organised by category
- `justfile` - Modern task runner with elegant commands
- `mise.lock` - Lock file for reproducible tool installations
- `build.py` - Pyinfra script executed during Docker build to install APT repos, packages, and mise tools

## Tool Management

- `mise outdated` - Check for tool updates
- `mise upgrade` - Upgrade all tools
- **Debian packages**: See `Dockerfile` for complete package list and repository setup
- **mise tools**: See `mise.toml` for tool definitions organised by category
