# Cloud Native Devcontainer

Cloud native development container with modern tooling for operations & development teams.

## About AGENTS.md

This file follows the [AGENTS.md standard](http://agents.md/) from OpenAI, now part of the [Agentic AI Foundation (AAIF)](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) under the Linux Foundation. It provides project-specific guidance for AI coding agents like [Goose](https://block.github.io/goose), Cursor, Copilot, and others.

## Philosophy: Grug-Brained Development

This repo follows ["grug-brained"](https://grugbrain.dev) principles. The goal is working software, not architectural purity.

1. **Complexity is the Enemy**
   - Complexity is cognitive debt. Always choose simpler over "correct."
   - If a solution feels clever, it's probably wrong.

2. **Locality of Behavior (LoB) is King**
   - All tool installation logic is in one place: `build.py`
   - Don't split configuration across multiple files without good reason
   - Co-locate related functionality

3. **WET > DRY**
   - A little duplication beats a bad abstraction.
   - Only abstract with 3+ identical cases AND an obvious pattern.

4. **Testing: Behavior Over Implementation**
   - Test that Docker-in-Docker works, not internal implementation
   - Test that tools are installed and functional
   - Test what users experience, not how it's built

5. **Boring Tech Wins**
   - Use battle-tested tools: Debian stable, official Docker CE, mise
   - Avoid shiny new things that add complexity
   - Factor code, not infrastructure

## Principles

- Every command has a `just` recipe—run `just` to list all available commands
- Keep the build simple: one `build.py` file manages all packages and tools
- Test locally with `just build` and `just test` before committing
- **Agent workflow**: Agents can run `just build` and `just test` locally, but should NOT run `just publish` (requires maintainer credentials)

## Quick Start

Run `just` to see all available commands. Most common workflows:

```bash
just build    # Build test image locally
just test     # Test Docker-in-Docker functionality
just dev      # Interactive development shell
```

## Architecture

- **Base Image**: `debian:stable-backports` (Debian 13 Trixie stable + backports)
- **Package Management**: Hybrid approach - Debian packages for official tools, mise for specialised tools
- **Docker**: Official Docker CE with manual Docker-in-Docker setup
- **Build System**: Modern Docker BuildKit with docker bake and optimised caching
- **Automation**: Pyinfra (`build.py`) handles repository setup and package installation during container build

## Project Structure

- `build.py` - **THE SOURCE OF TRUTH** - All APT repos, packages, and mise tools defined here
- `Dockerfile` - Minimal container build that runs `build.py`
- `docker-bake.hcl` - Declarative build configuration with SBOM & provenance
- `justfile` - Task automation - use `just` commands instead of raw docker commands
- `.devcontainer/` - VS Code devcontainer configuration

## Making Changes

### Adding Tools

**All tool installation happens in `build.py`**:

1. **APT packages**: Add to `APT_PACKAGES` list (organised by category)
2. **APT repos**: Add to `APT_REPOS` list (use extrepo where available)
3. **mise tools**: Add to `MISE_TOOLS` list (organised by category)

Example adding a new tool:
```python
# In build.py, find the relevant section:
MISE_TOOLS = (
    # AI & Development Tools
    + ["ubi:block/goose", ("pipx:litellm", {"version": "latest", "extras": ["proxy"], "uvx_args": "--with boto3"})]
    # Simple: "tool-name" -> becomes "tool-name" = "latest"
    # Complex: ("tool-name", {...dict...}) -> Python dict converted to TOML inline table
)
```

### Testing Changes

```bash
just build    # Build test image with your changes
just test     # Verify Docker-in-Docker works
just dev      # Interactive shell to test tools manually
```

### Code Style

- **Language**: Use Australian English spelling (organise vs organize, colour vs color, etc.)
- **Python**: Follows pyinfra patterns - operations grouped by purpose
- **Docker**: Modern BuildKit features, cache mounts, multi-stage optimisation
- **Supply chain security**: SBOM and enhanced provenance (`mode=max`) for all builds

## Tool Management

- All tools defined in `build.py` - check there for what's installed
- Tools are organised by category (Languages, Cloud, Security, Shell, AI, etc.)
- Debian packages for official tools (Docker, kubectl, terraform)
- mise for specialised tools (go, node, python, k9s, trivy, etc.)
- `mise outdated` - Check for tool updates (inside container)
- `mise upgrade` - Upgrade all tools (inside container)

## AI Tools

This devcontainer includes AI development tools:

- **goose**: AI coding agent CLI from Block (via ubi - native binary)
- **litellm[proxy]**: LLM proxy with unified API (via pipx with boto3 injected)

These tools work together:
- litellm provides unified interface to multiple LLM providers (OpenAI, Anthropic, AWS Bedrock, etc.)
- boto3 is automatically injected into litellm's environment for AWS Bedrock authentication
- goose provides the AI agent interface for coding assistance

## Troubleshooting

**Docker not starting**: Check `just test` output, ensure `--privileged --cgroupns=host` in run args  
**Tool missing**: Check `build.py` MISE_TOOLS or APT_PACKAGES lists  
**Build fails**: Run `just clean` then `just build` to clear cache  
**Permission issues**: Ensure `vscode` user is in docker group (handled by `build.py`)
