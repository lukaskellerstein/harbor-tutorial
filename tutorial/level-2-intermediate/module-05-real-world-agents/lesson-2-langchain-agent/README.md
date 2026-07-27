# LangChain Agent in Harbor

**Duration:** 45-60 minutes

## Overview

In this lesson, you will wrap a **LangChain v1** agent as a Harbor `BaseAgent` so it can be evaluated against Harbor tasks. The agent is built with `create_agent()`, LangChain v1's standard factory for ReAct-style agents, and the model is served by the LiteLLM proxy (Gemma 4).

The interesting part of the wrapper is not the agent loop — `create_agent()` owns that. It is the **tool**: a single `execute_command` that reaches into Harbor's task container.

## Prerequisites

- Completed Module 4 (Building Custom Agents)
- Completed Lesson 1 (Evaluating Claude Code)
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

### Why Wrap External Agents?

Harbor evaluates agents by giving them a task instruction and a container environment. Built-in agents like `claude-code` already know how to work with Harbor. But if you have an agent built with LangChain, LangGraph, or another framework, you need to wrap it as a `BaseAgent` so Harbor can orchestrate it.

### `create_agent()` Owns the Loop

LangChain v1 replaced the hand-rolled "call the LLM, check `tool_calls`, append `ToolMessage`, repeat" pattern with a factory:

```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[execute_command],
    system_prompt=SYSTEM_PROMPT,
)
```

It returns a compiled LangGraph graph that runs the ReAct loop — tool dispatch, message accumulation, and termination when the model stops calling tools. The wrapper never writes an iteration loop, and `recursion_limit` replaces the old `max_iterations` counter.

### Async Tools: No Bridging Needed

Harbor's `environment.exec()` is `async`. LangChain tools may be `async def`, and the graph executes them on the calling event loop when you use `ainvoke()`. So the tool simply awaits:

```python
@tool
async def execute_command(command: str) -> str:
    """Execute a shell command in the task environment container."""
    result = await environment.exec(command=command, timeout_sec=300)
    parts = [p for p in (result.stdout, result.stderr) if p]
    return "\n".join(parts) or "(no output)"
```

This is the whole Harbor integration. Note what is *absent*: no `asyncio.run_coroutine_threadsafe`, no `asyncio.to_thread`, no worker threads. If you have seen the thread-bridging pattern in older LangChain tutorials, it exists to serve *sync-only* tool interfaces — reach for it only when a framework gives you no async path.

### Models via the LiteLLM Proxy

The agent builds a `ChatOpenAI` client pointed at the gateway:

```python
llm = ChatOpenAI(
    model="gemma-large",                      # alias in infra/litellm/config.yaml
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
    api_key=os.environ.get("LITELLM_API_KEY", "sk-litellm-master"),
    temperature=0.0,
)
```

Switching provider or model is a config change in `infra/litellm/config.yaml`, never a code change here. The `-m` flag still works: `harbor run ... -m gemma-small` routes to the local 4B model.

### Agent Registration

Harbor loads custom agents via Python import paths:

```bash
harbor run -p tasks/coding-task --agent agent:LangchainHarborAgent -m gemma-large
```

The format is `module:ClassName` — Harbor imports the module and instantiates the class. `main.py` sets `PYTHONPATH` to the lesson directory so the `harbor` subprocess can import `agent`.

## Step-by-Step

### Step 1: Examine the Agent Wrapper

Open `agent.py`. `LangchainHarborAgent` extends `BaseAgent` and implements `name()`, `version()`, `setup()`, and `run()`. Inside `run()`:

- the async `execute_command` tool, closing over `environment`
- the `ChatOpenAI` client pointed at the LiteLLM gateway
- `create_agent(...)` and a single `await agent.ainvoke(...)`

### Step 2: Examine the Task

The `tasks/coding-task/` directory contains a task that asks the agent to write a Fibonacci function in Python. The test script imports the function and verifies correctness.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-2-langchain-agent
uv sync
uv run python main.py
```

### Step 4: Review Results

Results appear in the `jobs/` directory. Compare the LangChain agent's performance with Claude Code from Lesson 1.

## Expected Output

```
Step 2: Wrapping LangChain as a Harbor Agent
  LangChain v1's create_agent() owns the agent loop...

Step 4: Running Evaluation
  Running: harbor run -p tasks/coding-task --agent agent:LangchainHarborAgent -m gemma-large
  ...

Step 5: Results
  Task: tutorial/coding-task
  Reward: 1.0
```

## Key Takeaways

- Wrap any LangChain agent as a Harbor `BaseAgent` by implementing `name()`, `version()`, `setup()`, and `run()`
- `create_agent()` (LangChain v1) supplies the ReAct loop — don't hand-roll one; bound it with `recursion_limit`
- Async tools `await environment.exec()` directly; the thread-bridging pattern is only for sync-only frameworks
- All model traffic goes through the LiteLLM proxy under the `gemma-large` (Gemma 4) alias — provider changes are config changes, not code changes
- Register the agent with `--agent module:ClassName`

## Next Steps

In the next lesson, you will wrap a LangGraph stateful graph agent, which drops below `create_agent()` to build the graph — nodes, edges, and state — explicitly.
