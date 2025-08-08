FROM mcr.microsoft.com/devcontainers/base:bookworm

# Build arg for GitHub token
ARG GITHUB_TOKEN

# Debian essentials
RUN apt-get update && apt-get install -y python3-dev

# Switch to vscode user for tool installation
USER vscode
WORKDIR /home/vscode

# Set environment variable for mise
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

# Use login shell for subsequent RUN commands
SHELL ["/bin/bash", "-l", "-c"]

# Install mise
RUN curl https://mise.run/bash | sh
COPY --chown=vscode:vscode mise.toml ./
RUN mise trust && \
    for i in 1 2 3 4 5; do \
      if mise install; then break; fi; \
      echo "mise install failed, retrying in $((4 ** i)) seconds..."; \
      sleep $((4 ** i)); \
    done


# Switch back to root for any remaining setup
USER root
