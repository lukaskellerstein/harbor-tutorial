# Infrastructure Setup

This directory contains the Docker Compose services and verification script for the Harbor tutorial.

## Prerequisites

Before starting, make sure you have:

- **Python 3.12+** — `python --version`
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Docker** — installed and running
- **Harbor** — `uv tool install harbor`
- **Git** — for cloning benchmark repos

## Quick Start

### 1. Start Docker Compose services

```bash
cd infra
docker compose up -d
```

This starts:

| Service | Port | Purpose |
|---------|------|---------|
| **Qdrant** | 6333 (REST), 6334 (gRPC) | Vector database for RAG-based evaluation tasks |

### 2. Start LMStudio (optional)

LMStudio provides a local model server with an OpenAI-compatible API. It's needed for lessons that use local models.

```bash
lms server start
lms load google/gemma-4-e4b
```

The API will be available at `http://localhost:1234/v1`.

### 3. Verify everything

```bash
cd infra
uv sync
uv run python verify.py
```

## Service Details

### Qdrant

- **REST API**: http://localhost:6333
- **Dashboard**: http://localhost:6333/dashboard
- **gRPC**: localhost:6334

Data is persisted in a Docker volume (`qdrant-data`).

### LMStudio

LMStudio runs natively on your machine (not in Docker) because it needs GPU access.

- **API**: http://localhost:1234/v1
- **Docs**: https://lmstudio.ai/docs/cli

## Teardown

```bash
# Stop services (keep data)
docker compose down

# Stop services and delete all data
docker compose down -v
```

## Troubleshooting

### Docker not running
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Port conflicts
If ports 6333/6334 are in use, stop the conflicting service or edit `docker-compose.yaml` to remap ports.

### LMStudio model not loading
```bash
lms ls           # list available models
lms load --gpu max google/gemma-4-e4b
```
