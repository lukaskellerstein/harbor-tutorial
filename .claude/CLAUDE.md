# WORKFLOW — MANDATORY FOR ANY PROMPT THAT RESULTS IN CHANGES

**If you are going to use the Edit or Write tool, or run a command that changes
files, containers or Harbor jobs, you MUST complete the workflow in `rules/`
before reporting completion.** Applies to every type of work — a new lesson, a
fix to an existing one, infra changes, docs. No exceptions.

Steps, in order (each phase's detailed procedure is in the correspondingly-numbered
`rules/` file — already loaded into context, no need to open it):

1. **Understand** → [`rules/02-understand.md`](rules/02-understand.md)
2. **Plan** → [`rules/03-plan.md`](rules/03-plan.md) *(skip for trivial changes)*
3. **Implement** → [`rules/05-implement.md`](rules/05-implement.md)
4. **Test** → [`rules/06-testing.md`](rules/06-testing.md)
5. **Report** → [`rules/08-report.md`](rules/08-report.md)

Reference files: [`rules/01-project-config.md`](rules/01-project-config.md)
(the 48 lesson leaves, services and ports),
[`rules/09-code-quality.md`](rules/09-code-quality.md),
[`rules/10-tech-stack.md`](rules/10-tech-stack.md),
[`rules/11-communication.md`](rules/11-communication.md),
[`rules/12-security.md`](rules/12-security.md).

Project-specific references, all of them authoritative over the generic files
above where they overlap: [`rules/tutorial-structure.md`](rules/tutorial-structure.md),
[`rules/lesson-content.md`](rules/lesson-content.md),
[`rules/harbor-patterns.md`](rules/harbor-patterns.md),
[`rules/coding-standards.md`](rules/coding-standards.md),
[`rules/references.md`](rules/references.md).

**NEVER report completion without first running the affected lesson end-to-end
against a live Docker daemon.** "The code looks right" is not a test: a lesson
that imports cleanly but fails at `harbor` invocation, or scores every trial 0.0
because the test script path is wrong, looks identical to a working one until it
is run. Verification is YOUR responsibility — the user should never need to ask
you to test.

**Trivial changes** (a typo in a lesson README, a comment, a version bump in one
`pyproject.toml`): skip step 2. State what you'll do and proceed.

## harbor-tutorial at a glance

- **48 independently-runnable lesson leaves** under
  `tutorial/level-{1,2,3}-*/module-NN-*/lesson-N-*/`. This is deliberately **not**
  one project — each leaf owns its `pyproject.toml`, `.venv` and `.gitignore`, and
  there is no uv workspace.
- **Run a lesson** — `cd <lesson> && uv sync && uv run python main.py`. That is
  also how it is tested; there is no repo-wide test suite.
- **`syllabus.md`** at the root is the source of truth for which lessons exist,
  their topics and their ordering. Consult it before creating or modifying one.
- **Docker must be running.** Every Harbor evaluation is a container.
  `uv run python infra/verify.py` checks every prerequisite and reports OK/FAIL.
- **Support stack** — `cd infra && docker compose up -d` starts Qdrant (6333 REST,
  6334 gRPC) and the LiteLLM gateway (`${LITELLM_PORT:-4000}`). LMStudio runs
  natively on the host at 1234, not in a container — it needs GPU access.
- **Secrets** — every `.env` in this repo is gitignored and none is committed.
  `infra/.env.example` is the committed template for the support stack, and its
  hosted-provider keys are intentionally blank. Two lesson leaves under
  `module-05-real-world-agents` also read a leaf-local `.env` via `python-dotenv`
  for `CLAUDE_CODE_OAUTH_TOKEN` — an account-wide credential, so prefer letting
  `~/Projects/.envrc` deliver it from `~/.secrets/secrets.enc.yaml` and leave the
  leaf `.env` absent. See [`rules/12-security.md`](rules/12-security.md).
- **Harbor is CLI-first.** Most lessons shell out to `harbor`; the Python API is
  used only for custom agents and adapters.

Full facts → [`rules/01-project-config.md`](rules/01-project-config.md); stack and
conventions → [`rules/10-tech-stack.md`](rules/10-tech-stack.md).

## Standing authorizations — do NOT ask before doing these

These actions are pre-approved. Run them yourself when the situation calls for it.

### Read-only inspection (always safe)

- Reading any file in this repo, and the Harbor source at
  `~/Projects/Github/harbor-framework/harbor`
- `git status`, `git diff`, `git log`, `git show`
- `docker ps`, `docker images`, `docker compose ps`, `docker compose logs`
- `uv run harbor --help` and `uv run harbor <subcommand> --help`, **from inside a
  lesson leaf**. `harbor` is not on `$PATH`: it is a dependency of each leaf, so
  it resolves only through that leaf's `.venv`. Bare `harbor …` from the repo
  root is `command not found`.
- `uv run python infra/verify.py`
- `uv tree` / `uv pip list` inside a lesson leaf

Two CLIs from this machine's mac-setup are always on `PATH` (`~/.local/bin`):

- `nvim-tools --json --all` — every error, lint, formatting and type finding
  across this repo, one JSON envelope, from the same gated tools the editor
  runs. `--json` alone skips the slow type checker; `--status --path <file>`
  answers for one file; `--diff-all` previews the safe fixes without writing.
  A tool reporting `gated-off` has no config in this repo — that is the
  "no config, no tool" contract working, not a breakage.
- `lukas-ps --json [name]` — RAM/CPU of any process tree on this machine (the
  dev server, a test run, an editor); `[name]` filters by process name,
  `-p PID` filters to the tree owning that process.

`nvim-tools --fix-all` exists but **writes across the repo** — it is a
mutation, not inspection; run `--diff-all` and ask first unless it is listed
above as pre-approved.

### Pre-approved mutations

Each is scoped to a **named** target — a lesson leaf you state, or this repo's
own stack. None of them is a licence to act repo-wide.

- `uv sync` / `uv lock` inside one named lesson leaf
- Running a lesson end-to-end in a named leaf: `uv run python main.py`. This is
  the test step, and it will pull images and start containers.
- `harbor` trial and job runs against a task **inside this repo**
- `cd infra && docker compose up -d`, `docker compose restart <service>`,
  `docker compose logs` — this tutorial's own stack only
- Creating a new lesson directory under `tutorial/` when `syllabus.md` calls for
  it, following [`rules/tutorial-structure.md`](rules/tutorial-structure.md)

### Requires confirmation — always ask first

- `docker compose down -v`, or anything that removes the `qdrant-data` volume
- `docker system prune`, or removing any image this repo did not build
- Editing `infra/.env`, or any file under `~/.secrets`
- Changing the lesson list or ordering in `syllabus.md` — it is the source of
  truth, and lessons reference each other by number
- Deleting or renaming an existing lesson leaf
- Any edit spanning more than one lesson leaf

- `git push`, `git push --force`, branch deletes — **never commit unless the user
  explicitly asks**.
- Anything touching secrets, TLS material, tokens, or credential files. A secret
  never enters this repo in plaintext; if one must be versioned at all it is
  SOPS+age — [`rules/12-security.md`](rules/12-security.md).

When in doubt: ask. This is teaching material — a lesson that does not run
end-to-end is the first thing a learner hits, and they have no way to tell your
bug from their own mistake.

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

- **Source code**: ~/Projects/Github/harbor-framework/harbor
- **Docs**: <https://harborframework.com/docs>
- **Cookbook**: <https://github.com/harbor-framework/harbor-cookbook>

### LMStudio (local model serving)

- **CLI docs**: <https://lmstudio.ai/docs/cli>
- **Headless mode**: <https://lmstudio.ai/docs/developer/core/headless>
- **Selected model**: Gemma4-E4B — <https://lmstudio.ai/models/google/gemma-4-e4b>

### AI Agent Frameworks

| Framework | Source Code | Examples |
|-----------|------------|----------|
| Langchain | ~/Projects/Github/langchain-ai/langchain | ~/Projects/Github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/1_langchain |
| Langgraph | ~/Projects/Github/langchain-ai/langgraph | ~/Projects/Github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/2_langgraph |
| Deepagents | ~/Projects/Github/langchain-ai/deepagents | ~/Projects/Github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/3_deepagents |
| Claude Agent SDK | ~/Projects/Github/anthropics/claude-agent-sdk-python | ~/Projects/Github/lukaskellerstein/vibe-coding-course/5_Claude_Agent_SDK/python |

### RAG

- **Vector DB**: Qdrant

### Evaluation Benchmarks

- **SWE-Bench**: <https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified>

## Rules

1. **Consult `syllabus.md` first** — it is the source of truth for what lessons exist, their topics, and ordering.
2. **Consult Harbor source code before writing code** — do not guess at CLI flags, API signatures, or config formats. Read the source at `~/Projects/Github/harbor-framework/harbor`.
3. **Each lesson is self-contained** — a user runs `cd <lesson> && uv sync && uv run python main.py` and sees results. No shared state between lessons.
4. **Use `uv` for package management** — never `pip install`. Every lesson has its own `pyproject.toml`.
5. **Print meaningful console output** — section headers, progress, results. The user should be able to follow along by reading the terminal.
6. **Keep `main.py` under ~200 lines** — if a lesson needs helpers, put them in a separate module in the same directory.
7. **Harbor is CLI-first** — most lessons will invoke `harbor` via subprocess or instruct the user to run CLI commands. Python API is used only for custom agents and adapters.
8. **Docker must be running** — all Harbor evaluations run inside containers. Check and warn if Docker is not available.
9. **Modular rule files** are in `.claude/rules/`. They cover coding standards, Harbor patterns, lesson content format, references, and tutorial structure conventions.
