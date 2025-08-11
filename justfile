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
    docker buildx bake test --progress=plain

# Test Docker-in-Docker functionality
test: build
    @echo "🐳 Testing mise & Docker-in-Docker..."
    docker run --privileged --rm \
        --mount source={{docker_volume}},target=/var/lib/docker,type=volume \
        {{test_tag}} \
        -c "mise doctor && docker run --rm ghcr.io/curl/curl-container/curl-multi:master -s ipinfo.io && https ipinfo.io"

# Interactive development shell (build + test + shell)
dev: test
    @echo "🔓 Starting development shell..."
    docker run {{docker_args}} {{test_tag}}

# Publish to registry (build + push + sign)
publish:
    @echo "🚀 Building and publishing release image..."
    @echo "🔐 Authenticating with GHCR..."
    echo $GITHUB_TOKEN | docker login ghcr.io -u $(gh api user --jq .login) --password-stdin
    docker buildx bake release \
        --progress=plain \
        --set="release.tags={{tag}}"
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
    trivy image --config trivy.yaml {{test_tag}}

# Clean up images and volumes
clean:
    @echo "🧹 Cleaning up..."
    -docker rmi {{tag}} {{test_tag}}
    -docker volume rm {{docker_volume}}
    docker system prune -f
