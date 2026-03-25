# Cloud Native Devcontainer - Build & Development

# Auto-detect GITHUB_TOKEN from gh CLI to avoid API rate limits
export GITHUB_TOKEN := env("GITHUB_TOKEN", `gh auth token 2>/dev/null || echo ""`)

# Configuration
tag := "ghcr.io/wagov-dtt/devcontainer-base:latest"
test_tag := "devcontainer-base:test"
workspace := "/workspaces/devcontainer-base"

# Docker run args for interactive use (Docker-from-Docker via host socket)
docker_args := "-it --rm" + \
    " -v /var/run/docker.sock:/var/run/docker.sock" + \
    " --group-add " + `stat -c '%g' /var/run/docker.sock` + \
    " --mount type=bind,source=" + justfile_directory() + ",target=" + workspace + \
    " --workdir " + workspace

# Test command used by both local and CI (single source of truth)
test_cmd := "mise doctor && docker network create test-network && docker run --rm --network test-network ghcr.io/curl/curl-container/curl-multi:master -s ipinfo.io && https ipinfo.io && docker network rm test-network"

default:
    @just --list

# Validate generated config and CLI wiring
check:
    @uv run python -c 'import tomllib; from wagov_devcontainer.spec import MISE_TOML; tomllib.loads(MISE_TOML); print("TOML valid")'
    @uv run wagov-devcontainer --help >/dev/null
    @echo "CLI valid"

# Build Python distribution artifacts
package:
    rm -rf dist
    uv build

# Build test image locally
build: check
    @echo "Building test image..."
    docker buildx bake test --progress=plain

# Test Docker-from-Docker functionality
test: build
    @echo "Testing mise & Docker-from-Docker..."
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --group-add $(stat -c '%g' /var/run/docker.sock) \
        {{test_tag}} \
        -c "{{test_cmd}}"

# Print test command (for CI to use)
test-cmd:
    @echo "{{test_cmd}}"

# Interactive development shell (build + shell)
dev: build
    @echo "Starting development shell..."
    docker run {{docker_args}} {{test_tag}}

# Publish to registry (build + push, signing handled by bake attestations)
publish:
    @echo "Building and publishing release image..."
    @echo "Authenticating with GHCR..."
    echo $GITHUB_TOKEN | docker login ghcr.io -u $(gh api user --jq .login) --password-stdin
    docker buildx bake release \
        --progress=plain \
        --set="release.tags={{tag}}"

# Run published image
shell:
    @echo "Pulling latest image..."
    docker pull {{tag}}
    docker run {{docker_args}} --entrypoint bash {{tag}}

# Lint and format Python code
lint:
    @echo "Linting and formatting..."
    uv run ruff format build.py src
    uv run ruff check --fix build.py src

# Clean up images
clean:
    @echo "Cleaning up..."
    -docker rmi {{tag}} {{test_tag}}
    docker system prune -f
