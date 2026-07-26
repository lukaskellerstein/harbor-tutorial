# Deepagents in Harbor

**Duration:** 45-60 minutes

## Overview

Deepagents is a higher-level framework built on LangGraph by the LangChain team. It provides `create_deep_agent()` for one-call agent creation with built-in middleware for filesystem operations, memory, subagents, and more. In this lesson, you will wrap a Deepagents agent as a Harbor `BaseAgent` and evaluate it on a coding task.

## Prerequisites

- Completed Lesson 3 (Langgraph Agent in Harbor)
- Docker installed and running
- Harbor CLI installed
- `OPENAI_API_KEY` environment variable set

## Concepts

### Deepagents Architecture

Deepagents sits above LangGraph and provides:

- **create_deep_agent()** -- single function to create a fully configured agent
- **FilesystemMiddleware** -- built-in tools for reading and writing files
- **MemoryMiddleware** -- persistent memory across conversation turns
- **SubAgentMiddleware** -- spawn and coordinate sub-agents
- **RubricMiddleware** -- structured evaluation of agent outputs

### Tool Mapping for Harbor

Deepagents' built-in tools operate on the local filesystem. For Harbor evaluations, we need all operations to happen inside the task container. The solution: create custom Langchain tools that call `environment.exec()`:

| Deepagents built-in | Harbor equivalent |
|---------------------|-------------------|
| `write_file(path, content)` | `environment.exec("cat > path ...")` |
| `read_file(path)` | `environment.exec("cat path")` |
| `execute(command)` | `environment.exec(command)` |

### Graceful Fallback

The agent wrapper tries to import Deepagents' `create_deep_agent()` first. If the import fails (e.g., version mismatch or missing dependency), it falls back to a manual agent loop using the same tools. This pattern is useful for production wrappers.

## Step-by-Step

### Step 1: Understand the Agent Wrapper

Open `agent.py`. The `DeepagentsHarborAgent` class:

1. Creates `execute_command`, `write_file`, and `read_file` tools that bridge to `environment.exec()`
2. Tries to use `create_deep_agent()` from the Deepagents framework
3. Falls back to a manual LLM+tools loop if Deepagents is unavailable

### Step 2: Examine the Task

The `tasks/file-task/` requires creating a calculator module with four functions and a test script. This tests the agent's ability to write well-structured Python code.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/deepagents-agent
uv sync
export OPENAI_API_KEY=sk-...
uv run python main.py
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/deepagents-agent
uv sync
export OPENAI_API_KEY=sk-...
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

- Deepagents provides `create_deep_agent()` for simplified agent creation with middleware
- Map Deepagents' filesystem tools to Harbor's `environment.exec()` for container-based evaluation
- Use try/except with a fallback loop for robust agent wrappers
- Higher-level frameworks reduce boilerplate but add dependencies

## Next Steps

In the final lesson of this module, you will wrap the Claude Agent SDK, which runs Claude Code as a subprocess with programmatic control.
