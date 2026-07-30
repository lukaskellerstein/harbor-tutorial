# Harbor Tutorial Project

## What This Is

A hands-on tutorial teaching Harbor — the open-source framework for evaluating and optimizing AI agents and language models in container environments.

The full syllabus lives in `syllabus.md`. Always consult it before creating or modifying any lesson.

## Harbor Overview

Harbor evaluates arbitrary agents (Claude Code, OpenHands, Codex CLI, Aider, etc.) against benchmark tasks inside containers. Core concepts:

- **Task** — instruction + container environment + test script (unit of evaluation)
- **Dataset** — collection of tasks (usually corresponds to a benchmark)
- **Agent** — program that completes tasks
- **Environment** — container runtime (Docker, Daytona, Modal, E2B, etc.)
- **Trial** — single agent attempt at a task (produces a reward 0–1)
- **Job** — collection of trials

Install: `uv tool install harbor` or `pip install harbor`. Requires Python 3.12+ and Docker.

## Preferred Technologies & Local References

### Harbor (the subject of this tutorial)

- **Source code**: /Users/lkellers/Projects/github/harbor-framework/harbor
- **Docs**: <https://harborframework.com/docs>
- **Cookbook**: <https://github.com/harbor-framework/harbor-cookbook>

### LMStudio (local model serving)

- **CLI docs**: <https://lmstudio.ai/docs/cli>
- **Headless mode**: <https://lmstudio.ai/docs/developer/core/headless>
- **Selected model**: Gemma4-E4B — <https://lmstudio.ai/models/google/gemma-4-e4b>

### AI Agent Frameworks

| Framework | Source Code | Examples |
|-----------|------------|----------|
| Langchain | /Users/lkellers/Projects/github/langchain-ai/langchain | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/1_langchain |
| Langgraph | /Users/lkellers/Projects/github/langchain-ai/langgraph | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/2_langgraph |
| Deepagents | /Users/lkellers/Projects/github/langchain-ai/deepagents | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/3_deepagents |
| Claude Agent SDK | /Users/lkellers/Projects/github/anthropics/claude-agent-sdk-python | /Users/lkellers/Projects/github/lukaskellerstein/vibe-coding-course/5_Claude_Agent_SDK/python |

### RAG

- **Vector DB**: Qdrant

### Evaluation Benchmarks

- **SWE-Bench**: <https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified>

## Rules

1. **Consult `syllabus.md` first** — it is the source of truth for what lessons exist, their topics, and ordering.
2. **Consult Harbor source code before writing code** — do not guess at CLI flags, API signatures, or config formats. Read the source at `/Users/lkellers/Projects/github/harbor-framework/harbor`.
3. **Each lesson is self-contained** — a user runs `cd <lesson> && uv sync && uv run python main.py` and sees results. No shared state between lessons.
4. **Use `uv` for package management** — never `pip install`. Every lesson has its own `pyproject.toml`.
5. **Print meaningful console output** — section headers, progress, results. The user should be able to follow along by reading the terminal.
6. **Keep `main.py` under ~200 lines** — if a lesson needs helpers, put them in a separate module in the same directory.
7. **Harbor is CLI-first** — most lessons will invoke `harbor` via subprocess or instruct the user to run CLI commands. Python API is used only for custom agents and adapters.
8. **Docker must be running** — all Harbor evaluations run inside containers. Check and warn if Docker is not available.
9. **Modular rule files** are in `.claude/rules/`. They cover coding standards, Harbor patterns, lesson content format, references, and tutorial structure conventions.
