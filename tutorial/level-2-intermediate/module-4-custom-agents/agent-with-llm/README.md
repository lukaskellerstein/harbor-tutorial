# LLM-Powered Custom Agent

**Duration:** 45-60 minutes

## Overview

Learn how to build a custom Harbor agent that uses a large language model (LLM) to reason about tasks and generate solutions. This lesson demonstrates the agent-LLM-environment loop pattern, where the agent orchestrates between an LLM and the container environment.

## Prerequisites

- Completed Lesson 3: Prompt Templates
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- API key for an LLM provider (e.g., `ANTHROPIC_API_KEY`)

## Concepts

### The Agent-LLM-Environment Loop

Instead of hard-coding task solutions, an LLM-powered agent:

1. **Sends** the task instruction to an LLM
2. **Extracts** bash commands from the LLM's response
3. **Executes** the commands in the container via `environment.exec()`
4. **Checks** the result -- if it failed, sends the error back to the LLM
5. **Repeats** until success or max iterations

### self.model_name

The model name is passed via the `-m` CLI flag and available as `self.model_name` on the agent instance. It uses the LiteLLM convention: `provider/model-name`.

### LiteLLM

LiteLLM provides a unified API for calling any LLM provider:

```python
from litellm import acompletion

response = await acompletion(
    model="anthropic/claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Hello"}],
)
```

### When to Use LLM-Powered Agents

| Approach | Best For |
|----------|----------|
| Scripted agent (BaseAgent) | Simple, deterministic tasks |
| Installed agent | Tasks needing container-local tools |
| LLM-powered agent | Complex tasks requiring reasoning |

## Step-by-Step

### Step 1: Define the System Prompt

The system prompt tells the LLM how to format its responses (bash code blocks) and what tools are available in the container.

### Step 2: Implement the Loop

```python
for iteration in range(1, MAX_ITERATIONS + 1):
    response = await acompletion(model=self.model_name, messages=messages)
    commands = extract_bash_commands(response)
    result = await environment.exec(command=cmd)
    if result.return_code != 0:
        messages.append({"role": "user", "content": f"Error: {result.stderr}"})
    else:
        break
```

### Step 3: Extract and Execute Commands

Parse the LLM response for ```bash code blocks and execute each one.

### Step 4: Run the Evaluation

```bash
harbor run -p tasks/llm-task --agent agent:LLMAgent -m anthropic/claude-sonnet-4-5-20250929
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-4-custom-agents/agent-with-llm
uv sync
export ANTHROPIC_API_KEY=your-key-here
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 4, Lesson 4         #
#     LLM-Powered Custom Agent                         #
########################################################

============================================================
Step 1: The Agent-LLM-Environment Loop
============================================================
  Custom agents can integrate LLMs for reasoning about tasks...

============================================================
Step 2: The Loop Pattern
============================================================
    Agent                    LLM                  Container
      |--- instruction ------>|                       |
      |<-- bash commands -----|                       |
      |--- exec commands ---------------------------->|
      ...

============================================================
Step 6: Running the Evaluation
============================================================
  Running: harbor run -p tasks/llm-task --agent agent:LLMAgent -m ...
  [LLMAgent] Iteration 1/3
  [LLMAgent] Sending request to anthropic/claude-sonnet-4-5-20250929...
  [LLMAgent] All commands succeeded on iteration 1
```

## Key Takeaways

- LLM-powered agents use language models for reasoning about tasks
- The agent-LLM-environment loop: ask LLM -> execute -> check -> retry
- `self.model_name` receives the `-m` flag from the harbor CLI
- LiteLLM provides unified access to any model provider
- Iterative refinement with error feedback improves success rates

## Next Steps

You have completed **Module 4: Building Custom Agents**!

Next: **Module 5 -- Evaluating Real-World Agents** -- Learn to evaluate Claude Code, Langchain, Langgraph, and more.
