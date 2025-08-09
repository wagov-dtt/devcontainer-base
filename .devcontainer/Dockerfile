FROM ghcr.io/astral-sh/uv:bookworm

# Install system dependencies and Docker CE
RUN --mount=type=cache,target=/var/lib/apt/lists --mount=type=cache,target=/var/cache/apt \
    echo "deb http://deb.debian.org/debian bookworm-backports main" > /etc/apt/sources.list.d/backports.list \
    && apt-get update && apt-get dist-upgrade -y && apt-get install -y \
    ca-certificates curl gnupg sudo wget python3-dev tini && install -m 0755 -d /etc/apt/keyrings

# Add all GPG keys and repositories (organized by line length)
RUN add_repo() { curl -fsSL "$2" | gpg --dearmor -o "/etc/apt/keyrings/$1.gpg" && \
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/$1.gpg] $3" > "/etc/apt/sources.list.d/$1.list"; } \
    && add_repo "ddev" "https://pkg.ddev.com/apt/gpg.key" "https://pkg.ddev.com/apt/ * *" \
    && add_repo "mise" "https://mise.jdx.dev/gpg-key.pub" "https://mise.jdx.dev/deb stable main" \
    && add_repo "gcloud" "https://packages.cloud.google.com/apt/doc/apt-key.gpg" "https://packages.cloud.google.com/apt cloud-sdk main" \
    && add_repo "github" "https://cli.github.com/packages/githubcli-archive-keyring.gpg" "https://cli.github.com/packages stable main" \
    && add_repo "docker" "https://download.docker.com/linux/debian/gpg" "https://download.docker.com/linux/debian bookworm stable" \
    && add_repo "microsoft" "https://packages.microsoft.com/keys/microsoft.asc" "https://packages.microsoft.com/repos/azure-cli/ bookworm main" \
    && chmod a+r /etc/apt/keyrings/*.gpg

# Install Docker CE, mise, cloud CLIs, and developer tools
RUN --mount=type=cache,target=/var/lib/apt/lists --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
    mise azure-cli google-cloud-cli gh ddev bash-completion vim neovim fzf ripgrep ugrep btop tree htop

# Copy Docker configuration
COPY docker-init.sh /usr/local/bin/docker-init.sh

# Create vscode user with proper permissions
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && usermod -aG sudo,docker vscode \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Switch to vscode user for tool installation
USER vscode

# Copy mise configuration
COPY --chown=vscode:vscode mise.toml /home/vscode/.config/mise/config.toml

# Install tools with mise - use bash for exponentiation
RUN --mount=type=secret,id=GITHUB_TOKEN,env=GITHUB_TOKEN,uid=1000,gid=1000 \
    for i in 1 2 3 4 5; do \
      if mise install --yes; then break; fi; \
      delay=$((4*i)); \
      echo "mise install failed, retrying in ${delay} seconds..."; \
      sleep ${delay}; \
    done

# Configure shell enhancements for vscode user
RUN printf '\n# Shell enhancements\neval "$(mise activate bash)"\neval "$(starship init bash)"\n' >> /home/vscode/.bashrc 

ENV SHELL=/bin/bash \
    DOCKER_BUILDKIT=1

# Mount for docker-in-docker 
VOLUME [ "/var/lib/docker" ]

ENTRYPOINT ["tini", "--", "/usr/local/bin/docker-init.sh"]
CMD ["bash"]
