# devcontainer-base
Base devcontainer with common tooling

```bash
npm install -g @devcontainers/cli
curl https://mise.run/bash | sh
source ~/.bashrc
# Setup tools with `mise use` in the devcontainer-base subfolder
cd devcontainer-base
mise use just
cd ..
# Build the image
devcontainer build --workspace-folder devcontainer-base --image-name ghcr.io/wagov-dtt/devcontainer-base
```
