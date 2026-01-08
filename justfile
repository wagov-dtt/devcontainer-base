# Cloud Native Devcontainer - Build & Development

# Configuration
tag := "ghcr.io/wagov-dtt/devcontainer-base:latest"
test_tag := "devcontainer-base:test"
docker_volume := "dind-var-lib-docker"
workspace := "/workspaces/devcontainer-base"

# Docker run args for interactive use
docker_args := "--privileged --cgroupns=host -it --rm" + \
    " --mount source=" + docker_volume + ",target=/var/lib/docker,type=volume" + \
    " --mount type=bind,source=" + justfile_directory() + ",target=" + workspace + \
    " --workdir " + workspace

# Show available commands
default:
    @just --list

# Validate build.py generates valid TOML
check:
    @uvx --with pyinfra --with tomli python3 -c 'exec(open("build.py").read().split("config.SUDO")[0]); import tomli; tomli.loads(MISE_TOML); print("TOML valid")'

# Build test image locally  
build: check
    @echo "Building test image..."
    docker buildx bake test --progress=plain

# Test Docker-in-Docker functionality
test: build
    @echo "Testing mise & Docker-in-Docker..."
    docker run --privileged --cgroupns=host --rm \
        --mount source={{docker_volume}},target=/var/lib/docker,type=volume \
        {{test_tag}} \
        -c "mise doctor && docker network create test-network && docker run --rm --network test-network ghcr.io/curl/curl-container/curl-multi:master -s ipinfo.io && https ipinfo.io && docker network rm test-network"

# Interactive development shell (build + shell)
dev: build
    @echo "Starting development shell..."
    docker run {{docker_args}} {{test_tag}}

# Publish to registry (build + push + sign)
publish:
    @echo "Building and publishing release image..."
    @echo "Authenticating with GHCR..."
    echo $GITHUB_TOKEN | docker login ghcr.io -u $(gh api user --jq .login) --password-stdin
    docker buildx bake release \
        --progress=plain \
        --set="release.tags={{tag}}"
    @echo "Signing with cosign..."
    cosign sign --yes {{tag}}

# Run published image
shell:
    @echo "Pulling latest image..."
    docker pull {{tag}}
    docker run {{docker_args}} --entrypoint bash {{tag}}

# Security scan with Trivy
scan: build
    @echo "Security scanning..."
    trivy image --config trivy.yaml {{test_tag}}

# Lint and format Python code
lint:
    @echo "Linting and formatting..."
    uvx ruff format --line-length 200 build.py
    uvx ruff check --fix --select I --line-length 200 build.py

# Clean up images and volumes
clean:
    @echo "Cleaning up..."
    -docker rmi {{tag}} {{test_tag}}
    -docker volume rm {{docker_volume}}
    docker system prune -f
