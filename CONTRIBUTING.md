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

- `build.py` — source of truth for APT repos, APT packages, and mise tools
- `Dockerfile` — minimal image build that runs `build.py`
- `docker-bake.hcl` — BuildKit bake targets and image metadata
- `justfile` — common workflows; prefer `just` over raw docker commands
- `.devcontainer/` — VS Code devcontainer configuration

## Development Workflow

### Prerequisites

- Docker with BuildKit support
- [just](https://just.systems) command runner

### Common Commands

```bash
just              # List all commands
just build        # Build test image locally
just test         # Test Docker-from-Docker functionality
just dev          # Interactive development shell
just lint         # Format and lint Python files
just scan         # Security scan with Trivy
```

For maintainers only:

```bash
just publish      # Multi-platform build + push
just shell        # Run published image interactively
```

Do not run `just publish` unless you intend to publish and have the required credentials.

## Making Changes

### Adding Tools

All tool installation happens in `build.py`:

1. Add APT repos to `APT_REPOS` when an official signed repo exists
2. Add Debian packages to `APT_PACKAGES` when available
3. Add tools to `MISE_TOOLS` only when APT is unavailable or version flexibility matters

Prefer APT when possible. Signed distro or vendor packages are generally a better supply-chain choice than ad hoc downloads.

```python
# In build.py
MISE_TOOLS = (
    # Simple: "tool-name" -> becomes "tool-name" = "latest" in TOML
    + ["your-tool"]

    # Complex: tuple with TOML config string
    + [("pipx:tool", '{ version = "latest", extras = "extra" }')]
)
```

### Tool Source Priority

1. **APT via extrepo** — preferred for official signed packages
2. **mise** — use when APT is unavailable or too limiting

### Testing

Before submitting a PR:

1. Build succeeds: `just build`
2. Runtime test passes: `just test`
3. Lint passes: `just lint`
4. For tooling or shell changes, sanity check interactively with `just dev`

## Code Style

- Use Australian English spelling where practical
- Follow existing `build.py` pyinfra patterns
- Keep changes simple and local
- Favour clear duplication over clever abstraction
- Write commit messages that explain why, not just what

## Security and CI Notes

- Keep GitHub Actions pinned and up to date
- Prefer small, auditable workflow changes
- Test the user-facing behaviour inside the container, not just implementation details

## What to Contribute

- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance or security improvements

## Troubleshooting

| Issue | Solution |
|---|---|
| Docker not working | Ensure the host Docker socket is available |
| Tool missing | Check `build.py` `MISE_TOOLS` or `APT_PACKAGES` |
| Build fails | Run `just clean` then `just build` |
| Permission errors | Ensure the user is in the `docker` group |
| mise issues | Run `mise doctor` inside the container |
