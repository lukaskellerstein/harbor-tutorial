# Deepagents in Harbor

**Duration:** 45-60 minutes

## Overview

Deepagents is a higher-level framework built on LangGraph by the LangChain team. It is **batteries-included**: `create_deep_agent()` ships with planning (`write_todos`), filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`), shell execution (`execute`), and sub-agent delegation (`task`) — no custom tool definitions needed. In this lesson, you wrap a Deepagents agent as a Harbor `BaseAgent` by implementing a **backend** that routes all of those built-in tools into the task container, and serve the model through the LiteLLM proxy (Gemma 4).

## Prerequisites

- Completed Lesson 3 (Langgraph Agent in Harbor)
- Docker installed and running
- Harbor CLI installed
- The LiteLLM gateway from `agent-eval-benchmark/infra` running:

  ```bash
  cd agent-eval-benchmark/infra && podman compose up -d
  # for the local model aliases: lms server start && lms load google/gemma-4-e4b
  ```

  The gateway serves Gemma 4 under friendly aliases (see `infra/litellm/config.yaml`):
  `gemma-large` (26B, used here), `gemma-small` / `gemma-local` (4B via LMStudio).
  No provider API key is needed in this lesson — the proxy holds the keys.

## Concepts

### Deepagents Is Batteries-Included

`create_deep_agent()` gives the agent these tools out of the box:

- **write_todos** — plan and track multi-step work
- **ls, read_file, write_file, edit_file, glob, grep** — file operations
- **execute** — run shell commands
- **task** — spawn and delegate to sub-agents

The mistake to avoid: re-implementing `write_file`/`read_file` as custom LangChain tools. That discards the framework's tested tool schemas, prompts, and middleware.

### Backends: the Integration Point

Built-in tools operate through a pluggable **backend** (`SandboxBackendProtocol`). By default files live in graph state or on the local filesystem — but Harbor needs everything to happen inside the task container. Deepagents' `BaseSandbox` base class derives *all* file tools from three primitives, so the whole Harbor bridge is:

| Backend primitive | Harbor equivalent |
|-------------------|-------------------|
| `execute(command)` | `environment.exec(command)` |
| `upload_files([(path, bytes)])` | `environment.exec("... base64 -d > path")` |
| `download_files([path])` | `environment.exec("base64 < path")` |

Implement those three in a `BaseSandbox` subclass (`HarborSandboxBackend` in `agent.py`), pass it as `backend=` to `create_deep_agent()`, and every built-in tool — including `edit_file`, `glob`, and `grep`, which you never wrote — operates inside the container.

### Models via the LiteLLM Proxy

The agent builds a `ChatOpenAI` client pointed at the gateway:

```python
llm = ChatOpenAI(
    model="gemma-large",                      # alias in infra/litellm/config.yaml
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
    api_key=os.environ.get("LITELLM_API_KEY", "sk-litellm-master"),
)
```

Switching provider or model is a config change in `infra/litellm/config.yaml`, never a code change here. The `-m` flag still works: `harbor run ... -m gemma-small` routes to the local 4B model.

## Step-by-Step

### Step 1: Understand the Agent Wrapper

Open `agent.py`. Two classes:

1. `HarborSandboxBackend(BaseSandbox)` — implements `execute()`, `upload_files()`, `download_files()`, and `id` against `environment.exec()`. File content crosses the boundary base64-encoded so shell quoting can't corrupt it.
2. `DeepagentsHarborAgent(BaseAgent)` — builds the LiteLLM-backed `ChatOpenAI`, calls `create_deep_agent(model=..., backend=...)` with **no custom tools**, and runs it with `ainvoke()`.

### Step 2: Examine the Task

The `tasks/file-task/` requires creating a calculator module with four functions and a test script. This tests the agent's ability to write well-structured Python code.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-4-deepagents-agent
uv sync
uv run python main.py
```

## Expected Output

```
Step 2: Understanding Deepagents
  Deepagents (by LangChain) is a higher-level framework...

Step 4: Running Evaluation
  ...

Step 5: Results
  Task: tutorial/file-task
  Reward: 1.0
```

## Key Takeaways

- Deepagents is batteries-included — planning, file ops, execute, and sub-agents ship with `create_deep_agent()`; don't re-implement its tools
- The backend, not the tool list, is the integration point: subclass `BaseSandbox`, implement `execute`/`upload_files`/`download_files`, and every built-in tool routes through Harbor's container
- All model traffic goes through the LiteLLM proxy under the `gemma-large` (Gemma 4) alias — provider changes are config changes, not code changes

## Next Steps

In the final lesson of this module, you will wrap the Claude Agent SDK, which runs Claude Code as a subprocess with programmatic control.
