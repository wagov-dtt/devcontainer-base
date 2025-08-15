FROM debian:stable-backports AS builder

ENV DEBIAN_FRONTEND=noninteractive DOCKER_BUILDKIT=1

# Setup repos and install packages
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update -qq && apt-get install -yqq curl gnupg ca-certificates apt-utils >/dev/null && install -m 0755 -d /etc/apt/keyrings && \
    add_repo() { curl -LsSf "$2" | gpg --dearmor -o "/etc/apt/keyrings/$1.gpg" && \
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/$1.gpg] $3" > "/etc/apt/sources.list.d/$1.list"; } && \
    add_repo "ddev" "https://pkg.ddev.com/apt/gpg.key" "https://pkg.ddev.com/apt/ * *" && \
    add_repo "mise" "https://mise.jdx.dev/gpg-key.pub" "https://mise.jdx.dev/deb stable main" && \
    add_repo "helm" "https://baltocdn.com/helm/signing.asc" "https://baltocdn.com/helm/stable/debian/ all main" && \
    add_repo "gcloud" "https://packages.cloud.google.com/apt/doc/apt-key.gpg" "https://packages.cloud.google.com/apt cloud-sdk main" && \
    add_repo "github" "https://cli.github.com/packages/githubcli-archive-keyring.gpg" "https://cli.github.com/packages stable main" && \
    add_repo "docker" "https://download.docker.com/linux/debian/gpg" "https://download.docker.com/linux/debian trixie stable" && \
    add_repo "microsoft" "https://packages.microsoft.com/keys/microsoft.asc" "https://packages.microsoft.com/repos/azure-cli/ bookworm main" && \
    add_repo "hashicorp" "https://apt.releases.hashicorp.com/gpg" "https://apt.releases.hashicorp.com bookworm main" && \
    chmod a+r /etc/apt/keyrings/*.gpg

ARG DATE TARGETARCH
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt/lists \
    echo "Build date: ${DATE:-$(date +%F)}, Architecture: ${TARGETARCH:-amd64}" && \
    apt-get update -qq && apt-get dist-upgrade -yqq >/dev/null && apt-get install -yqq \
        docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
        mise azure-cli google-cloud-cli gh ddev terraform helm neovim fzf ripgrep ugrep btop htop restic rclone \
        git wget bash-completion sudo python3-dev tini build-essential openssh-client less jq unzip zip file rsync \
        iputils-ping dnsutils net-tools procps lsof locales librsvg2-bin iptables >/dev/null && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen && \
    update-alternatives --set iptables /usr/sbin/iptables-legacy && \
    update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

# Create vscode user and install mise tools
RUN groupadd --gid 1000 vscode && \
    useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode && \
    usermod -aG sudo,docker vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/vscode && \
    chmod 0440 /etc/sudoers.d/vscode

USER vscode
COPY --chown=vscode:vscode mise.toml /home/vscode/.config/mise/config.toml

RUN --mount=type=cache,target=/home/vscode/.cache,uid=1000,gid=1000 \
    --mount=type=secret,id=GITHUB_TOKEN,env=GITHUB_TOKEN,uid=1000,gid=1000 \
    for i in 1 2 3 4 5; do \
      if UV_LINK_MODE=copy mise install --quiet --yes; then break; fi; \
      echo "mise install failed, retrying in $((4*i)) seconds..."; \
      sleep $((4*i)); \
    done

# Configure shell
RUN cat >> /home/vscode/.bashrc << 'EOF'

# Shell enhancements
eval "$(mise activate bash)"
eval "$(starship init bash)"
mise reshim

# Docker-in-Docker initialization
start_docker() {
    if ! mountpoint -q /var/lib/docker 2>/dev/null; then return 0; fi
    if ! test -r /proc/1/cgroup 2>/dev/null; then return 0; fi
    if pgrep -x dockerd >/dev/null 2>&1; then return 0; fi
    sudo dockerd >/tmp/dockerd.log 2>&1 &
    local timeout=30
    while ((timeout-- > 0)); do
        if docker version >/dev/null 2>&1; then return 0; fi
        sleep 1
    done
    echo "Error: Docker failed to start within 30 seconds" >&2
    return 1
}
start_docker
EOF

# Final stage
FROM scratch
COPY --from=builder --link / /

ENV DOCKER_BUILDKIT=1 TZ=Australia/Perth EDITOR=nvim TERM=xterm-256color COLORTERM=truecolor

USER vscode
VOLUME [ "/var/lib/docker" ]
ENTRYPOINT ["tini", "--", "bash", "-il"]
