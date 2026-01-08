FROM debian:stable-backports AS builder

ENV DEBIAN_FRONTEND=noninteractive DOCKER_BUILDKIT=1

# Copy build file
COPY build.py ./

# Install pipx and run pyinfra build in one step
# Use cache mounts to speed up rebuilds when only tool configs change
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/root/.cache,sharing=locked \
    --mount=type=cache,target=/home/vscode/.cache,sharing=locked \
    --mount=type=secret,id=GITHUB_TOKEN,env=GITHUB_TOKEN \
    apt-get update -y && apt-get install -y pipx sudo && \
    SETUP_USER=vscode pipx run build.py

# Final stage
FROM scratch
COPY --from=builder --link / /

ENV DOCKER_BUILDKIT=1 TZ=Australia/Perth EDITOR=nvim TERM=xterm-256color COLORTERM=truecolor

USER vscode
VOLUME [ "/var/lib/docker" ]
ENTRYPOINT ["tini", "--", "bash", "-il"]
