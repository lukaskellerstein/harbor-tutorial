# Claude Agent SDK in Harbor

**Duration:** 45-60 minutes

## Overview

The Claude Agent SDK provides programmatic access to Claude Code through a Python API. Unlike the Langchain and LangGraph wrappers (which build their own agent loops), the SDK runs Claude Code as a subprocess, giving you access to its full tool suite and agentic capabilities. In this lesson, you will wrap the SDK as a Harbor `BaseAgent` using MCP servers to route tool calls into the container.

## Prerequisites

- Completed Lesson 4 (Deepagents in Harbor)
- Docker installed and running
- Harbor CLI installed
- `ANTHROPIC_API_KEY` environment variable set
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)

## Concepts

### How the Claude Agent SDK Works

The SDK runs Claude Code as a local subprocess:

```
Your Python code
     |
Claude Agent SDK (query() function)
     |
Claude Code CLI (subprocess)
     |
Anthropic API (Claude model)
```

The `query()` function yields `Message` objects as the agent works: `AssistantMessage` (text and tool calls), `UserMessage` (tool results), and `ResultMessage` (final summary with cost).

### MCP Integration for Harbor

The challenge: the SDK runs Claude Code on the host, but Harbor tasks execute inside containers. Solution: create an in-process MCP server with a `container_exec` tool:

```python
@tool("container_exec", "Execute in container", {"command": str})
async def container_exec(args):
    result = await environment.exec(command=args["command"])
    return {"content": [{"type": "text", "text": result.stdout}]}

server = create_sdk_mcp_server("harbor-env", tools=[container_exec])
```

### Permission Mode

For unattended evaluations, set `permission_mode="bypassPermissions"`. This allows Claude Code to execute all tools without asking for user confirmation.

### Cost Tracking

The `ResultMessage` at the end of each query includes `total_cost_usd` -- useful for tracking evaluation costs across multiple agents and tasks.

## Step-by-Step

### Step 1: Understand the Agent Wrapper

Open `agent.py`. The `ClaudeSDKHarborAgent`:

1. Creates an MCP tool (`container_exec`) that routes to `environment.exec()`
2. Creates an SDK MCP server with `create_sdk_mcp_server()`
3. Configures `ClaudeAgentOptions` with the MCP server and `bypassPermissions`
4. Iterates over `query()` results, logging cost information

### Step 2: Examine the Task

The `tasks/coding-task/` asks the agent to build a word counter script that reads a sample file and produces a report with word counts.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/claude-sdk-agent
uv sync
export ANTHROPIC_API_KEY=sk-ant-...
uv run python main.py
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/claude-sdk-agent
uv sync
export ANTHROPIC_API_KEY=sk-ant-...
uv run python main.py
```

## Expected Output

```
Step 2: Understanding the Claude Agent SDK
  The Claude Agent SDK provides programmatic access to Claude Code...

Step 4: Running Evaluation
  Running: harbor run -p tasks/coding-task --agent agent:ClaudeSDKHarborAgent ...
  ...

Step 5: Results
  Task: tutorial/word-counter-task
  Reward: 1.0
```

## Key Takeaways

- The Claude Agent SDK runs Claude Code as a subprocess with programmatic control
- Use `create_sdk_mcp_server()` to create in-process tools that route to Harbor's container
- Set `permission_mode="bypassPermissions"` for unattended evaluation
- Disable built-in tools and only allow your MCP tool to keep operations inside the container
- `ResultMessage.total_cost_usd` provides cost tracking for evaluations
- The SDK approach is the most "batteries included" -- Claude Code handles planning, error recovery, and tool orchestration

## Next Steps

Congratulations on completing Module 5! You now know how to evaluate agents from five different frameworks in Harbor. In Module 6, you will learn about creating datasets and working with benchmarks.
