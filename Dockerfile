FROM debian:stable-backports AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG DATE

ENV DOCKER_BUILDKIT=1 TZ=Australia/Perth EDITOR=nvim TERM=xterm-256color COLORTERM=truecolor

COPY mise.toml mise.apt.toml ./
COPY scripts/ ./scripts/

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=GITHUB_TOKEN,env=GITHUB_TOKEN \
    set -eu && \
    # Install base packages needed for bootstrapping
    apt-get update -y && apt-get install -y curl ca-certificates extrepo gnupg locales sudo && \
    locale-gen en_US.UTF-8 && \
    # Install mise
    curl --proto '=https' --tlsv1.2 -sSf https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh && \
    # Enable extrepo contrib/non-free policies, then vendor repos
    sed -i 's/^# - contrib/- contrib/' /etc/extrepo/config.yaml && \
    sed -i 's/^# - non-free/- non-free/' /etc/extrepo/config.yaml && \
    for repo in docker-ce github-cli kubernetes google_cloud ddev mise hashicorp; do \
      extrepo enable "$repo" || echo "extrepo: $repo skipped or already enabled"; \
    done && \
    # Install APT system packages via mise bootstrap
    mise bootstrap packages install --yes --update -E apt && \
    # Create docker group and vscode user
    groupadd docker && \
    useradd -m -s /bin/bash -G sudo,docker vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vscode && \
    chmod 440 /etc/sudoers.d/vscode && \
    # Install Docker init script
    install -m 755 scripts/docker-init.sh /usr/local/bin/docker-init.sh && \
    # Run user-space bootstrap as vscode: tools, dotfiles
    sudo -Hu vscode mise trust --yes / && \
    sudo -Hu vscode mise bootstrap --yes

FROM scratch
COPY --from=builder --link / /

USER vscode
ENTRYPOINT ["tini", "--", "bash", "-il"]
