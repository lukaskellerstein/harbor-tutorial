# Multi-Container Tasks

**Duration:** 40-50 minutes

## Overview

Standard Harbor tasks run inside a single Docker container, but real-world scenarios often require multiple services -- a web API with a database, a frontend with a backend and cache, or a microservice mesh. This lesson teaches you how to create Harbor tasks that use Docker Compose to run multiple containers, and how agents interact with individual services.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Completed Module 7, Lesson 1 (Docker Environments)
- Harbor installed (`uv tool install harbor`)
- Docker and Docker Compose installed and running
- Basic knowledge of Docker Compose

## Concepts

### When to Use Multi-Container Tasks

Use multi-container tasks when your evaluation scenario requires:
- A database (PostgreSQL, MySQL, Redis, etc.)
- Multiple communicating services (API + worker + queue)
- Integration testing across service boundaries
- Realistic deployment topologies

### The `main` Service Convention

Harbor requires every docker-compose.yaml to define a service named **`main`**. This is where the agent runs. All other services are "sidecars" that provide supporting infrastructure.

Harbor overlays your docker-compose.yaml with its own compose files to:
- Inject environment variables into the `main` service
- Mount volumes for the `main` service
- Set CPU/memory resource limits
- Add egress control (network isolation)

The layering order is: resource limits, base compose, your task compose, extra overlays, env vars, mounts, and optionally an egress control sidecar.

### Service Interaction API

`BaseEnvironment` provides methods for interacting with specific services:

```python
# Execute a command in a sidecar service
result = await environment.service_exec(
    command="pg_isready",
    service="db",
)

# Download a file from a sidecar
await environment.service_download_file(
    source_path="/var/log/app.log",
    target_path="./app.log",
    service="db",
)

# Download a directory from a sidecar
await environment.service_download_dir(
    source_dir="/app/output/",
    target_dir="./output/",
    service="db",
)

# Stop a sidecar service
await environment.stop_service(service="db")
```

When `service` is `None` or `"main"`, these methods delegate to the regular `exec()`, `download_file()`, and `download_dir()` methods.

Important: sidecar execs use `sh -c` (not `bash -c`) since sidecars may not have bash installed. They also do not inherit the main container's workdir, default user, or persistent environment variables.

### Artifact Collection with Sidecars

Harbor's trial orchestrator supports phased artifact collection:
1. Run main-service collect hooks
2. Download artifacts from the main service
3. Optionally stop the main service (prevents agent tampering)
4. Run sidecar collect hooks
5. Download artifacts from sidecar services

The `ArtifactConfig` in task.toml supports a `service` field to specify which compose service to collect artifacts from.

### Cloud Provider Support

Multi-container tasks work with cloud providers that support Docker Compose. Providers like Modal, GKE, Novita, and Islo use a Docker-in-Docker topology: the Docker daemon runs inside a cloud sandbox, and compose services run within it.

## Step-by-Step

### Step 1: Understand the Task Structure

The lesson includes a complete multi-service task in `tasks/multi-service/` with:
- A Flask API service (the `main` service where the agent runs)
- A PostgreSQL database sidecar
- An instruction asking the agent to create a user via the API and verify it in the database

### Step 2: Study the Docker Compose Configuration

The `docker-compose.yaml` defines two services: `main` (Flask API) and `db` (PostgreSQL). The database includes a health check so the API waits for it to be ready.

### Step 3: Examine the Flask API

The API (`environment/api/app.py`) provides endpoints for creating and listing users. It connects to PostgreSQL via the `DATABASE_URL` environment variable.

### Step 4: Review the Database Schema

The `init.sql` script creates a `users` table and seeds it with one existing user. PostgreSQL runs this automatically on first start.

### Step 5: Understand Service Interaction

The lesson explains how agents use `service_exec()`, `service_download_file()`, and `service_download_dir()` to interact with specific services in the compose environment.

### Step 6: Review the Test Script and Solution

The test script queries the database directly to verify the agent created the expected user. The solution script shows the oracle approach using curl and psql.

### Step 7: Try Running the Task

If Docker is running, you can run the task with the oracle agent to validate the setup.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-12-advanced-workflows/lesson-2-multi-container
uv sync
uv run python main.py
```

To run the actual task (requires Docker):

```bash
# Validate with the oracle agent
harbor trial start \
    -p tasks/multi-service \
    -a oracle \
    -m "anthropic/claude-sonnet-4-5-20250929"

# Explore interactively
harbor task start-env \
    -p tasks/multi-service \
    -e docker -i
```

## Expected Output

```
============================================================
  Multi-Container Tasks with Docker Compose
============================================================

This lesson demonstrates how to create Harbor tasks that run
multiple services using Docker Compose. We build a task with
a Flask API backed by a PostgreSQL database.

Harbor: harbor x.y.z
Docker: running

============================================================
  Step 1: Why Multi-Container Tasks?
============================================================

Standard Harbor tasks run inside a single Docker container.
But many real-world tasks need multiple services:
...

============================================================
  Step 3: Docker Compose Configuration
============================================================

File: tasks/multi-service/environment/docker-compose.yaml

services:
  main:
    build:
      context: ./api
    ...

  db:
    image: postgres:16-alpine
    ...

============================================================
  Step 6: Agent Interaction with Services
============================================================

IMPORTANT: Harbor requires one service named 'main' in every
docker-compose.yaml. This is where the agent runs. Additional
services are called 'sidecars'.
...
```

## Key Takeaways

- Multi-container tasks use `docker-compose.yaml` in the `environment/` directory instead of a single Dockerfile.
- Harbor requires a service named `main` -- this is where the agent runs. Other services are sidecars.
- Harbor overlays your compose file with its own files for env vars, volumes, resource limits, and egress control.
- Use `service_exec()`, `service_download_file()`, and `service_download_dir()` to interact with specific services.
- Sidecar execs use `sh` (not `bash`) and do not inherit the main container's workdir or environment.
- Cloud providers (Modal, GKE, etc.) support multi-container tasks via Docker-in-Docker.

## Next Steps

Continue to the next lesson: [Harbor Hub](../lesson-3-harbor-hub/) to learn how to share datasets, upload results, and compete on leaderboards.
