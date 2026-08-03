---
description: Project configuration — architecture, paths, dev environment
---

# Project Config

<!-- Filled from what the repo actually contains. Every line must be verifiable
     by reading a file in the repo — never write an aspiration here. Delete any
     bullet that does not apply rather than leaving a placeholder. -->

- **Project**: harbor-tutorial — a hands-on tutorial teaching Harbor, the
  open-source framework for evaluating AI agents and LLMs in containers
- **Architecture**: 48 independently-runnable lesson leaves plus a shared
  `infra/` support stack. No application; the lessons *are* the deliverable.
- **Structure**: `tutorial/level-{1,2,3}-*/module-NN-*/lesson-N-*/` (the
  lessons), `infra/` (docker-compose + `verify.py`), `syllabus.md` (the source
  of truth for lesson list and ordering)
- **Build**: nothing is built. `uv sync` in a leaf resolves that leaf's
  dependencies against its own `.venv`.
- **Run locally**: `cd <lesson> && uv sync && uv run python main.py` → console
  output; Harbor writes results under that leaf's gitignored `jobs/`
- **Test**: no repo-wide suite. Running the lesson end-to-end against a live
  Docker daemon *is* the test — see `06-testing.md`.
- **Key dependencies**: `harbor` (CLI-first; `uv tool install harbor`), Docker,
  and per-lesson extras (langchain, langgraph, deepagents, claude-agent-sdk,
  qdrant-client, datasets) declared in each leaf's own `pyproject.toml`
- **Package manager**: `uv`, always. Never `pip install`.

## Leaves

This repo is **not one project**. Each leaf below is independently runnable and
keeps its own environment — no workspaces, by design.

| Leaf | Count | Notes |
|:--|:--|:--|
| `infra/` | 1 | docker-compose stack + `verify.py` prerequisite checker |
| `tutorial/level-1-foundations/` | 11 | modules 01–03: getting started, tasks, running evaluations |
| `tutorial/level-2-intermediate/` | 22 | modules 04–08: custom agents, real-world agents, datasets, environments, grading |
| `tutorial/level-3-advanced/` | 14 | modules 09–12: adapters, scaling, analysis, advanced workflows |

Every leaf carries its own `pyproject.toml` (with `[tool.ruff]`), `uv.lock`,
`.gitignore` and `.venv`. `pyrightconfig.json` at the root has one
`executionEnvironments` entry per leaf pointing at that leaf's `.venv` — that is
what stops basedpyright reporting spurious unresolved imports across the tree.
**Re-run `~/Projects/Github/lukaskellerstein/mac-setup/projects/scripts/gen-pyrightconfig.py`
when a leaf is added**, and diff before committing.

A lesson leaf's internal shape:

```text
lesson-N-<name>/
├── main.py                      the runnable entrypoint (< ~200 lines)
├── README.md                    the lesson text — format in lesson-content.md
├── pyproject.toml               deps + [tool.ruff]
├── uv.lock
├── jobs/                        gitignored — Harbor's trial output
└── tasks/<task-name>/
    ├── task.toml                task definition
    ├── instruction.md           what the agent is asked to do
    ├── environment/Dockerfile   the container the trial runs in
    ├── solution/solve.sh        the oracle solution
    └── tests/test.sh            the verifier — decides the 0–1 reward
```

## Services and ports

Started with `cd infra && docker compose up -d`.

| Service | Port | Purpose |
|:--|:--|:--|
| Qdrant | 6333 (REST), 6334 (gRPC) | vector DB for RAG-based evaluation tasks |
| LiteLLM gateway | `${LITELLM_PORT:-4000}` | one OpenAI-compatible endpoint in front of LMStudio + hosted providers |
| LMStudio | 1234 | **runs natively on the host, not in a container** — it needs GPU access |

`uv run python infra/verify.py` checks every prerequisite (Python, uv, Docker,
harbor, git-lfs, and the services above) and prints OK/FAIL per item. Run it
first when anything behaves oddly.

Config for the stack comes from `infra/.env`, which is **gitignored**;
`infra/.env.example` is the committed template and `docker-compose.yaml` supplies
defaults for everything except the hosted-provider keys.
