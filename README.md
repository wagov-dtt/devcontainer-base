# devcontainer-base
This devcontainer includes essential development tools for cloud-native and infrastructure development, including [AWS](https://aws.amazon.com/cli/)/[Azure](https://docs.microsoft.com/en-us/cli/azure/)/[GCP](https://cloud.google.com/sdk/gcloud) CLIs, Kubernetes tools ([kubectl](https://kubernetes.io/docs/reference/kubectl/), [helm](https://helm.sh/), [k9s](https://k9scli.io/)), programming runtimes ([Go](https://golang.org/), [Node.js](https://nodejs.org/), [Python](https://www.python.org/)), infrastructure tools ([Terraform](https://www.terraform.io/), [Trivy](https://trivy.dev/)), and productivity utilities ([jq](https://jqlang.github.io/jq/), [just](https://just.systems/), [zellij](https://zellij.dev/)). All tools are pre-installed and configured for immediate use in development workflows.

## Setup
```bash
npm install -g @devcontainers/cli
curl https://mise.run/bash | sh
source ~/.bashrc
# Setup tools with `mise use` in the devcontainer-base subfolder
cd devcontainer-base
mise use just
cd ..
# Build the image with tools included by dockerfile
devcontainer build --workspace-folder devcontainer-base
```

## Local Development
```bash
# Build locally (with optional GitHub token to avoid rate limits)
export GITHUB_TOKEN=your_token_here
devcontainer build --workspace-folder devcontainer-base --image-name devcontainer-base:local

# Security scan with Trivy
trivy image devcontainer-base:local

# Test the container
docker run -it --rm --user vscode devcontainer-base:local bash

# Test tools are installed (copy/paste friendly)
docker run --rm --user vscode devcontainer-base:local bash -l -c 'mise list'
```
