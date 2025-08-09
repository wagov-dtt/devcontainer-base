# Cloud Native Devcontainer - Build & Development

# Configuration
tag := "ghcr.io/wagov-dtt/devcontainer-base:latest"
test_tag := "devcontainer-base:test"
docker_volume := "dind-var-lib-docker"
workspace := "/workspaces/devcontainer-base"

# Docker run args for interactive use
docker_args := "--privileged -it --rm" + \
    " --mount source=" + docker_volume + ",target=/var/lib/docker,type=volume" + \
    " --mount type=bind,source=" + justfile_directory() + ",target=" + workspace + \
    " --workdir " + workspace

# Show available commands
default:
    @just --list

# Build test image locally
build:
    @echo "🔨 Building test image..."
    cd .devcontainer && DOCKER_BUILDKIT=1 docker build \
        --secret id=GITHUB_TOKEN \
        --progress=plain \
        -t {{test_tag}} \
        -f Dockerfile ..

# Test Docker-in-Docker functionality
test: build
    @echo "🐳 Testing Docker-in-Docker..."
    docker run --privileged --rm \
        --mount source={{docker_volume}},target=/var/lib/docker,type=volume \
        {{test_tag}} \
        bash -c "sleep 10 && docker --version && docker info && docker run hello-world"

# Interactive development shell (build + test + shell)
dev: test
    @echo "🔓 Starting development shell..."
    docker run {{docker_args}} {{test_tag}}

# Publish to registry (build + push + sign)
publish:
    @echo "🚀 Building release image..."
    cd .devcontainer && DOCKER_BUILDKIT=1 docker build \
        --secret id=GITHUB_TOKEN \
        --progress=plain \
        -t {{tag}} \
        -f Dockerfile ..
    @echo "🔐 Authenticating with GHCR..."
    echo $GITHUB_TOKEN | docker login ghcr.io -u $(gh api user --jq .login) --password-stdin
    @echo "📤 Publishing..."
    docker push {{tag}}
    @echo "🔏 Signing with cosign..."
    cosign sign --yes {{tag}}

# Run published image
shell:
    @echo "📥 Pulling latest image..."
    docker pull {{tag}}
    docker run {{docker_args}} --entrypoint bash {{tag}}

# Security scan with Trivy
scan: build
    @echo "🔍 Security scanning..."
    trivy image {{test_tag}}

# Clean up images and volumes
clean:
    @echo "🧹 Cleaning up..."
    -docker rmi {{tag}} {{test_tag}}
    -docker volume rm {{docker_volume}}
    docker system prune -f
