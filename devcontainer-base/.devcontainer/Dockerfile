FROM mcr.microsoft.com/devcontainers/base:bookworm

# Switch to vscode user for tool installation
USER vscode
WORKDIR /home/vscode

# Use login shell for subsequent RUN commands
SHELL ["/bin/bash", "-l", "-c"]

# Install mise
RUN curl https://mise.run/bash | sh
COPY --chown=vscode:vscode mise.toml ./
RUN mise trust && mise install

# Switch back to root for any remaining setup
USER root
