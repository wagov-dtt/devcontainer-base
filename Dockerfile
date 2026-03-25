FROM debian:stable-backports AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG DATE

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=GITHUB_TOKEN,env=GITHUB_TOKEN \
    apt-get update -y && apt-get install -y pipx sudo && \
    SETUP_USER=vscode pipx run --spec . wagov-devcontainer

FROM scratch
COPY --from=builder --link / /

ENV DOCKER_BUILDKIT=1 TZ=Australia/Perth EDITOR=nvim TERM=xterm-256color COLORTERM=truecolor

USER vscode
ENTRYPOINT ["tini", "--", "bash", "-il"]
