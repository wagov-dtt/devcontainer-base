# Contributing to devcontainer-base

Thanks for your interest in contributing.

## Quick Start

1. Fork and clone the repository
2. Make your changes
3. Test locally: `just build && just test && just dev`
4. Submit a pull request

## Philosophy

This repo follows [grug-brained development](https://grugbrain.dev):

- Complexity is the enemy
- Locality of behaviour is king
- A little duplication beats a bad abstraction
- Test behaviour over implementation details
- Boring tech wins

## Project Structure

| File | Purpose |
|---|---|
| `mise.toml` | Core config: settings, 60+ tools, dotfiles, tasks |
| `mise.apt.toml` | APT bootstrap packages + extrepo hooks (Debian/Ubuntu) |
| `mise.brew.toml` | Brew bootstrap packages (macOS, atomic Linux) |
| `Dockerfile` | Container build: installs mise, runs `mise bootstrap -E apt` |
| `install.sh` | Host installer: platform detection → mise bootstrap |
| `scripts/docker-init.sh` | Docker socket group synchronisation |
| `docker-bake.hcl` | BuildKit bake targets and image metadata |
| `justfile` | Development workflows (`just build`, `just test`, etc.) |
| `.devcontainer/` | VS Code devcontainer configuration |

## Development Workflow

### Prerequisites

- Docker with BuildKit support
- [just](https://just.systems) command runner (also installed by mise)

### Common Commands

```bash
just              # List all commands
just build        # Build test image locally
just test         # Test Docker-outside-of-Docker functionality
just dev          # Interactive development shell
just lint         # Lint project files (shell, TOML, workflows)
just fmt          # Format project files
```

For maintainers only:

```bash
just release 2026.7 # Create and push release tag; CI publishes images
just shell        # Run published image interactively
```

Do not create release tags unless you intend to publish images and have confirmed CI is green.

## Making Changes

### Adding Tools

1. Add APT system packages to `mise.apt.toml` under `[bootstrap.packages]` with `apt:` prefix, and brew equivalents to `mise.brew.toml` with `brew:` prefix
2. Add development tools to `mise.toml` under `[tools]`

Prefer APT/brew system packages for system-level tools. Use mise for dev tools that need version flexibility or aren't available in system repos.

```toml
# mise.toml — development tools
[tools]
"pipx:tool" = "latest"
"cargo:tool" = "latest"
"npm:tool" = "latest"
tool = "latest"              # mise default registry

# mise.apt.toml — Debian/Ubuntu system packages
[bootstrap.packages]
"apt:your-package" = "latest"

# mise.brew.toml — macOS/brew system packages
[bootstrap.packages]
"brew:your-formula" = "latest"
```

### Tool Source Priority

1. **APT via extrepo** - preferred for official signed packages
2. **Homebrew** - user-space packages on macOS or atomic Linux hosts
3. **mise** - use when system packages are unavailable or too limiting

### Testing

Before submitting a PR:

1. Validate config: `just check`
2. Build succeeds: `just build`
3. Runtime test passes: `just test`
4. Lint passes: `just lint`
5. For tooling or shell changes, sanity check interactively with `just dev`

## Code Style

- Use Australian English spelling where practical
- Keep changes simple and local
- Favour clear duplication over clever abstraction
- Write commit messages that explain why, not just what

## Security and CI Notes

- Keep GitHub Actions pinned and up to date
- Prefer small, auditable workflow changes
- Test the user-facing behaviour inside the container, not just implementation details

## Release Process

Releases are image-only. Do not add Python packaging files, PyPI workflows, or version fields for releases.

1. Ensure `main` is up to date and CI is green: `git pull --ff-only && gh run list --branch main --limit 5`
2. Create an annotated tag: `git tag -a v2026.7 -m "Release v2026.7"`
3. Push it: `git push origin v2026.7`
4. Optionally create GitHub release notes: `gh release create v2026.7 --title v2026.7 --notes "Container image release v2026.7"`

The build workflow publishes per-architecture images plus a multi-arch manifest for the tag.

## What to Contribute

- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance or security improvements

## Troubleshooting

| Issue | Solution |
|---|---|
| Docker not working | Ensure the host Docker socket is available |
| Tool missing | Check `mise.toml` |
| Build fails | Run `just clean` then `just build` |
| Permission errors | Ensure the user is in the `docker` group |
| mise issues | Run `mise doctor` inside the container |
