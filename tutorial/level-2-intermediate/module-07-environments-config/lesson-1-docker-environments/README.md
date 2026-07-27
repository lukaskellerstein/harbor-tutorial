# Docker Environments

**Duration:** 30-40 minutes

## Overview

Every Harbor task runs inside a Docker container defined by a Dockerfile. This lesson explores three Dockerfile strategies -- simple Ubuntu, language-specific Python, and multi-stage Go builds -- and teaches best practices for building efficient, purpose-built environments for your evaluation tasks.

## Prerequisites

- Completed Level 1 (Modules 1-3)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### Why Dockerfiles Matter for Harbor

The Dockerfile in your task's `environment/` directory defines what the agent has to work with. A well-designed Dockerfile:

- **Builds fast** -- smaller base images and fewer layers mean quicker iteration
- **Contains the right tools** -- the agent can only use what is installed in the container
- **Is reproducible** -- anyone can rebuild the exact same environment

### Three Approaches

1. **Simple Ubuntu base** (`ubuntu:24.04`): Maximum compatibility. Use when your task needs general Linux tools or you are unsure what the agent will need. Larger image, but everything "just works."

2. **Language-specific base** (`python:3.12-slim`): Smaller image with the language runtime pre-installed. Use when your task is language-specific. The `-slim` variants cut image size significantly.

3. **Multi-stage build** (builder stage + runtime stage): Compile code in one stage, copy only the binary to a minimal runtime stage. Use for compiled languages (Go, Rust, C/C++) to keep the final image small.

### Dockerfile Best Practices for Harbor

- Use `WORKDIR /app` for a predictable agent workspace
- Install only what the task requires
- Use `--no-install-recommends` with apt-get
- Clean up caches (`rm -rf /var/lib/apt/lists/*`)
- Pre-populate test data with `COPY` or `RUN echo`
- Use slim/alpine base images when possible

## Step-by-Step

### Step 1: Examine the Three Dockerfiles

The lesson includes three tasks, each with a different Dockerfile approach. Review each one to understand the trade-offs.

**Ubuntu task** (`tasks/ubuntu-task/environment/Dockerfile`):
```dockerfile
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl lsb-release ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
```

**Python task** (`tasks/python-task/environment/Dockerfile`):
```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir requests==2.32.3
WORKDIR /app
RUN echo '{"sample": "data", "count": 42}' > /app/sample_data.json
```

**Multi-stage task** (`tasks/multistage-task/environment/Dockerfile`):
```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /build
RUN cat > main.go << 'EOF'
package main
import "fmt"
func main() { fmt.Println("Hello from a multi-stage Docker build!") }
EOF
RUN CGO_ENABLED=0 GOOS=linux go build -o greeter main.go

FROM alpine:3.20
RUN apk add --no-cache bash
WORKDIR /app
COPY --from=builder /build/greeter /app/greeter
```

### Step 2: Run Each Task with the Oracle Agent

The lesson runs all three tasks with the oracle agent to verify they build correctly and produce the expected results.

### Step 3: Compare Build Times and Image Sizes

After running, the lesson reports build times and (where available) image sizes so you can see the trade-offs in practice.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-07-environments-config/lesson-1-docker-environments
uv sync
uv run python main.py
```

## Expected Output

```
Step 1: Three Dockerfile Approaches for Harbor Tasks

  1. Simple Ubuntu Base Image
     Base image: ubuntu:24.04
     Strategy:   General-purpose OS image with apt-get installs

  2. Language-Specific Python Image
     Base image: python:3.12-slim
     Strategy:   Slim language runtime with pip installs

  3. Multi-Stage Go Build
     Base image: golang:1.22-alpine -> alpine:3.20
     Strategy:   Build in one stage, run in a minimal stage

...

Step 5: Results Summary

  Task                           Status     Time
  ------------------------------ ---------- ----------
  Simple Ubuntu Base Image       PASS       12.3s
  Language-Specific Python Image PASS       8.7s
  Multi-Stage Go Build           PASS       15.1s
```

(Exact times will vary based on your system and whether images are cached.)

## Key Takeaways

- Match your base image to the task's language and tools
- Prefer slim/alpine variants to reduce build time and image size
- Multi-stage builds keep build tools out of the runtime image, producing smaller final images
- Always set `WORKDIR /app` for a predictable agent workspace
- Pre-populate data files so the agent has everything it needs inside the container

## Next Steps

Continue to [Environment Capabilities](../lesson-2-environment-features/) to learn the BaseEnvironment API -- `exec()`, file operations, and path checks.
