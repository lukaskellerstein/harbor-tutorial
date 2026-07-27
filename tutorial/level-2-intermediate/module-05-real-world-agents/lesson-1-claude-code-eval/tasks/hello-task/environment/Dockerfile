FROM ubuntu:24.04
WORKDIR /app

# Pre-install what the Claude Code installer needs. A bare ubuntu image has no
# curl or CA certificates, so agent setup had to run apt-get update first --
# that pushed setup past Harbor's 360s limit and raised AgentSetupTimeoutError.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*
