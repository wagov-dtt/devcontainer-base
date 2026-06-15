# Cloud Native Devcontainer - Build & Development

# Auto-detect GITHUB_TOKEN from gh CLI to avoid mise/GitHub API rate limits during builds.
export GITHUB_TOKEN := env("GITHUB_TOKEN", `gh auth token 2>/dev/null || echo ""`)

# Configuration
tag := "ghcr.io/wagov-dtt/devcontainer-base:latest"
test_tag := "devcontainer-base:test"
workspace := "/workspaces/devcontainer-base"

# Docker run args for interactive use (Docker-outside-of-Docker via host socket)
docker_args := "-it --rm" + \
    " -v /var/run/docker.sock:/var/run/docker.sock" + \
    " --group-add " + `stat -c '%g' /var/run/docker.sock` + \
    " --mount type=bind,source=" + justfile_directory() + ",target=" + workspace + \
    " --workdir " + workspace

default:
    @just --list

# Validate mise configuration
check:
    @mise trust --yes && mise config >/dev/null && echo "Config valid"

# Build test image locally
build: check
    @echo "Building test image..."
    docker buildx bake test --progress=plain

# Test Docker-outside-of-Docker functionality
test: build
    @echo "Testing mise & Docker-outside-of-Docker..."
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --group-add $(stat -c '%g' /var/run/docker.sock) \
        {{test_tag}} \
        -c 'network="devcontainer-test-$(date +%s)-$$"; trap "docker network rm \"$network\" >/dev/null 2>&1 || true" EXIT; docker network create "$network" >/dev/null && mise --version && docker run --rm --network "$network" ghcr.io/curl/curl-container/curl-multi:master -s ipinfo.io && https ipinfo.io'

# Print test command (for CI to use)
test-cmd:
    @printf '%s\n' 'network="devcontainer-test-$(date +%s)-$$"; trap "docker network rm \"$network\" >/dev/null 2>&1 || true" EXIT; docker network create "$network" >/dev/null && mise --version && docker run --rm --network "$network" ghcr.io/curl/curl-container/curl-multi:master -s ipinfo.io && https ipinfo.io'

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

# Lint project files
lint:
    @echo "Linting..."
    @mise exec -- shfmt -d scripts/*.sh install.sh 2>/dev/null || true
    @mise exec -- shellcheck -x scripts/*.sh install.sh 2>/dev/null || true
    @mise exec -- taplo fmt --check mise*.toml 2>/dev/null || true

# Format project files
fmt:
    @echo "Formatting..."
    @mise exec -- shfmt -w scripts/*.sh install.sh
    @mise exec -- taplo fmt mise*.toml

# Clean up images
clean:
    @echo "Cleaning up..."
    -docker rmi {{tag}} {{test_tag}}
    docker system prune -f
