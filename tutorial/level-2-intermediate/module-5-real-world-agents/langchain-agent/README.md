# Langchain Agent in Harbor

**Duration:** 45-60 minutes

## Overview

In this lesson, you will wrap a Langchain ReAct agent as a Harbor `BaseAgent` so it can be evaluated against Harbor tasks. The key challenge is bridging Langchain's synchronous tool interface with Harbor's asynchronous `environment.exec()` API.

## Prerequisites

- Completed Module 4 (Building Custom Agents)
- Completed Lesson 1 (Evaluating Claude Code)
- Docker installed and running
- Harbor CLI installed
- `OPENAI_API_KEY` environment variable set (for OpenAI models)

## Concepts

### Why Wrap External Agents?

Harbor evaluates agents by giving them a task instruction and a container environment. Built-in agents like `claude-code` already know how to work with Harbor. But if you have an agent built with Langchain, Langgraph, or another framework, you need to wrap it as a `BaseAgent` so Harbor can orchestrate it.

### The Async/Sync Bridge

This is the central challenge of wrapping Langchain agents:

- **Harbor's API is async**: `environment.exec()` is an `async` method
- **Langchain tools are sync**: tool functions decorated with `@tool` are regular (non-async) functions

The solution uses Python's asyncio threading utilities:

```python
loop = asyncio.get_running_loop()

def run_async_in_thread(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=120)

@langchain_tool
def execute_command(command: str) -> str:
    result = run_async_in_thread(environment.exec(command=command))
    return result.stdout or ""
```

### Agent Registration

Harbor loads custom agents via Python import paths:

```bash
harbor run -p tasks --agent agent:LangchainHarborAgent -m openai/gpt-4o
```

The format is `module:ClassName` -- Harbor imports the module and instantiates the class.

## Step-by-Step

### Step 1: Examine the Agent Wrapper

Open `agent.py` to see how `LangchainHarborAgent` extends `BaseAgent`. Pay attention to:

- The `execute_command` tool that bridges to `environment.exec()`
- The async/sync bridging with `run_coroutine_threadsafe`
- The simple agent loop: LLM call -> tool execution -> repeat

### Step 2: Examine the Task

The `tasks/coding-task/` directory contains a task that asks the agent to write a Fibonacci function in Python. The test script imports the function and verifies correctness.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/langchain-agent
uv sync
export OPENAI_API_KEY=sk-...
uv run python main.py
```

### Step 4: Review Results

Results appear in the `jobs/` directory. Compare the Langchain agent's performance with Claude Code from Lesson 1.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/langchain-agent
uv sync
export OPENAI_API_KEY=sk-...
uv run python main.py
```

## Expected Output

```
Step 2: Wrapping Langchain as a Harbor Agent
  The key challenge: Langchain tools are synchronous, but Harbor's
  environment.exec() is async...

Step 4: Running Evaluation
  Running: harbor run -p tasks/coding-task --agent agent:LangchainHarborAgent -m openai/gpt-4o
  ...

Step 5: Results
  Task: tutorial/coding-task
  Reward: 1.0
```

## Key Takeaways

- Wrap any Langchain agent as a Harbor `BaseAgent` by implementing `name()`, `version()`, `setup()`, and `run()`
- Bridge sync Langchain tools to async Harbor calls using `asyncio.run_coroutine_threadsafe()`
- Use `asyncio.to_thread()` to run sync Langchain LLM calls without blocking
- Register the agent with `--agent module:ClassName`
- The same pattern works for any sync agent framework

## Next Steps

In the next lesson, you will wrap a Langgraph stateful graph agent, which adds explicit state management and graph-based control flow.
