# Infrastructure Setup

This directory contains the Docker Compose services and verification script for the Harbor tutorial.

## Prerequisites

Before starting, make sure you have:

- **Python 3.12+** — `python --version`
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Docker** — installed and running
- **Harbor** — `uv tool install harbor`
- **Git** — for cloning benchmark repos
- **Git LFS** — `brew install git-lfs && git lfs install` (required for Hugging Face datasets, which store large files via LFS)

## Quick Start

### 1. Start Docker Compose services

```bash
cd infra
cp .env.example .env    # then fill in OPENROUTER_API_KEY — see LiteLLM below
docker compose up -d
```

This starts:

| Service | Port | Purpose |
|---------|------|---------|
| **Qdrant** | 6333 (REST), 6334 (gRPC) | Vector database for RAG-based evaluation tasks |
| **LiteLLM** | 4000 | OpenAI-compatible gateway used by every LLM judge (Module 8) |

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

- **REST API**: <http://localhost:6333>
- **Dashboard**: <http://localhost:6333/dashboard>
- **gRPC**: localhost:6334

Data is persisted in a Docker volume (`qdrant-data`).

### LiteLLM gateway

Module 8 (Grading & Rewards) grades open-ended agent output with LLM judges. Every one of those calls goes through this proxy rather than to a provider directly, so **which model does the judging is a config change here, never a code change in a lesson**.

- **API**: <http://localhost:4000/v1> (OpenAI-compatible)
- **Auth**: send `LITELLM_MASTER_KEY` as the bearer token (default `sk-litellm-master`)
- **Config**: [`litellm/config.yaml`](litellm/config.yaml)

#### Available aliases

| Alias | Backed by | Cost | Notes |
|-------|-----------|------|-------|
| `gemma-large` | OpenRouter `gemma-4-26b-a4b-it:free` | free | **Default judge for Module 8.** Needs `OPENROUTER_API_KEY`. |
| `gemma-local` | LMStudio `google/gemma-4-e4b` | free | Fully offline. Needs LMStudio running on the host. |
| `gemma-26b` / `gemma-31b` | OpenRouter, paid tier | ~$0.12–0.14 / 1M in | Fallback targets when the free tier rate-limits. |
| `gpt-mini` | OpenAI `gpt-5.4-mini` | metered | Last link in the fallback chain. Needs `OPENAI_API_KEY`. |

`gemma-large` falls back automatically: `gemma-26b` → `gemma-31b` → `gpt-mini`.

#### Reaching the gateway from a task container

Harbor runs tasks inside Docker, so `localhost` inside the container is not your machine. Use the host gateway hostname:

```toml
# task.toml
[verifier.env]
OPENAI_API_BASE = "http://host.docker.internal:4000/v1"
OPENAI_API_KEY  = "${LITELLM_MASTER_KEY:-sk-litellm-master}"
```

Docker Desktop on macOS and Windows resolves `host.docker.internal` automatically. On Linux, add `--add-host=host.docker.internal:host-gateway` or use your host's LAN IP.

#### Checking it works

```bash
# List every alias the gateway serves
curl -s http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-litellm-master"

# Send a real completion through an alias
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-master" \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma-large","messages":[{"role":"user","content":"say hi"}]}'
```

#### Swapping the judge model

Two ways, no code change either way:

1. **Permanently** — repoint the alias in `litellm/config.yaml` and `docker compose restart litellm`.
2. **For one run** — override it at the RewardKit level: `REWARDKIT_JUDGE=openai/gemma-local` (or `rewardkit --judge ...`). This wins over whatever the task's judge TOML says.

### LMStudio

LMStudio runs natively on your machine (not in Docker) because it needs GPU access.

- **API**: <http://localhost:1234/v1>
- **Docs**: <https://lmstudio.ai/docs/cli>

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

If ports 6333/6334/4000 are in use, stop the conflicting service or edit `docker-compose.yaml` to remap ports.

### LMStudio model not loading

```bash
lms ls           # list available models
lms load --gpu max google/gemma-4-e4b
```

### LiteLLM returns 401

The proxy rejects requests without the master key. Check that the token you send matches `LITELLM_MASTER_KEY` in `.env`, and note that `docker compose restart litellm` is required after changing it.

### A judge scores 0 with an error in `reward-details.json`

RewardKit asks for strict JSON-schema output. If the model behind the alias cannot produce it, `drop_params: true` silently drops the request for structured output and the model answers in prose, which RewardKit cannot parse.

```bash
docker compose logs litellm --tail 50    # see which route actually served the call
```

Fix by pointing at a stronger judge for that run:

```bash
REWARDKIT_JUDGE=openai/gpt-mini uv run python main.py
```
