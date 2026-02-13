# Contributing to devcontainer-base

Thanks for your interest in contributing!

## Quick Start

1. Fork and clone the repository
2. Make your changes
3. Test: `just build && just test && just dev`
4. Submit a pull request

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

## Making Changes

### Adding Tools

All tool installation happens in `build.py`:

1. **APT packages**: Add to `APT_PACKAGES` list (organised by category)
2. **APT repos**: Add to `APT_REPOS` list (use extrepo where available)
3. **mise tools**: Add to `MISE_TOOLS` list

```python
# In build.py
MISE_TOOLS = (
    # Simple: "tool-name" -> becomes "tool-name" = "latest" in TOML
    + ["your-tool"]
    # Complex: ("tool-name", '{ version = "latest", extras = "extra" }')
    + [("pipx:tool", '{ version = "latest", extras = "proxy" }')]
)
```

### Code Style

- **Language**: Use Australian English spelling (organise, colour, etc.)
- **Python**: Follow existing patterns in `build.py`
- **Commit messages**: Concise, focus on "why" not "what"

### Testing

Before submitting a PR:

1. Build succeeds: `just build`
2. Tests pass: `just test`
3. Lint passes: `just lint`

## What to Contribute

- New tools or tool updates
- Documentation improvements
- Bug fixes
- Performance optimisations

## Philosophy

This project follows [grug-brained development](https://grugbrain.dev):

- Complexity is the enemy
- Locality of behaviour is king
- A little duplication beats a bad abstraction
- Boring tech wins

See [AGENTS.md](AGENTS.md) for detailed guidance.
