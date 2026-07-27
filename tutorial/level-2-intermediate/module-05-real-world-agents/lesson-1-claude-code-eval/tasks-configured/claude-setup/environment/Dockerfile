FROM python:3.12-slim
WORKDIR /app

# Pre-install what the Claude Code installer needs, so agent setup does not
# have to run apt-get update before it can download anything.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# The MCP SDK, for the local stdio server below. Installed at build time so the
# task needs no network while the agent is running.
RUN pip install --no-cache-dir mcp

# Every piece of Claude Code configuration, baked into the image at project
# scope. /app is the WORKDIR, so this is exactly the layout Claude Code reads
# on your own machine -- Harbor needs no flags and no job.yaml entries for any
# of it.
#
# The Docker build context is this environment/ directory, so every COPY
# source has to live inside it.
COPY claude/     /app/.claude/
COPY CLAUDE.md   /app/CLAUDE.md
COPY mcp.json    /app/.mcp.json
COPY mcp_server/ /app/mcp_server/
