---
description: "Reference: Technology stack — Python 3.12+ / uv / Docker / Harbor, CLI-first"
---

# Reference: Technology Stack

<!-- Read from manifests (package.json, pyproject.toml, go.mod, Chart.yaml),
     never guessed. Pin the versions that actually constrain choices; omit the
     ones that do not. Delete sections that do not apply. -->

## Backend

- **Language**: Python, `requires-python = ">=3.12"` in every leaf. Harbor itself
  requires 3.12+, so this is a hard floor, not a preference.
- **Framework**: none — Harbor is **CLI-first**. Lessons invoke the `harbor`
  binary via `subprocess`, or instruct the learner to run it. The Python API is
  used only for custom agents and adapters (modules 04, 09).
- **Data**: Qdrant v1.14.0 (vector DB, RAG evaluation tasks). Harbor's own run
  output is plain JSON on disk under each leaf's gitignored `jobs/`.
- **Model access**: LiteLLM proxy as one OpenAI-compatible endpoint, fronting
  LMStudio (local, GPU, host-native) with OpenRouter and OpenAI as the fallback
  chain. Aliases and the chain are in `infra/litellm/config.yaml`.

## Infrastructure

- **Deploy**: nothing deploys. `infra/docker-compose.yaml` runs the local support
  stack and that is the whole of it.
- **Runtime**: Docker on the host — required, not optional. Every Harbor trial
  runs in its own container built from the task's `environment/Dockerfile`.
  Cloud environments (Daytona, Modal, E2B) appear as *subject matter* in module
  10; the repo itself only needs local Docker.

## Scripting & Automation

- Default: **Python** for anything a lesson runs, consistent with the rest of the
  stack
- Shell scripts only for trivial one-liners — with one deliberate exception:
  every task's `solution/solve.sh` and `tests/test.sh` are shell by Harbor's own
  contract, since they execute *inside* the task container where Python may not
  be present

## Package management

- **`uv`, always. Never `pip install`.** Each leaf has its own `pyproject.toml`
  and `uv.lock`, resolved into its own `.venv`.
- Harbor itself is installed as a tool, outside any leaf:
  `uv tool install harbor`
- There is **no workspace** — see `01-project-config.md` § Leaves. Adding one
  would break the "clone, cd in, run it" property every lesson depends on.

## Conventions this machine imposes

- **One formatter per filetype.** Biome owns the JS/TS family; prettier and
  eslint are not installed. Python formats with the ruff CLI chain.
- Tools run only where the repo carries their config file — see
  `rules/09-code-quality.md`.
