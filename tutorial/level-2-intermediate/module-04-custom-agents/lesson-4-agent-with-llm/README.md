# LLM-Powered Custom Agent

**Duration:** 45-60 minutes

## Overview

Learn how to build a custom Harbor agent that uses a large language model (LLM) to reason about tasks and generate solutions. This lesson demonstrates the agent-LLM-environment loop pattern, where the agent orchestrates between an LLM and the container environment.

This is the first lesson in the module where a **real model** is in the loop. Lessons 1-3 hard-code their solutions on purpose, so you can study the Harbor lifecycle without LLM behaviour in the way. Here the solution is genuinely generated.

## Prerequisites

- Completed Lesson 3: Prompt Templates
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- The LiteLLM gateway from `agent-eval-benchmark/infra` running:

  ```bash
  cd agent-eval-benchmark/infra && podman compose up -d
  # for the local model aliases: lms server start && lms load google/gemma-4-e4b
  ```

  The gateway serves Gemma 4 under friendly aliases (see `infra/litellm/config.yaml`):
  `gemma-large` (26B, used here), `gemma-small` / `gemma-local` (E4B via LMStudio).
  No provider API key is needed in this lesson — the proxy holds the keys.

## Concepts

### The Agent-LLM-Environment Loop

Instead of hard-coding task solutions, an LLM-powered agent:

1. **Sends** the task instruction to an LLM
2. **Extracts** bash commands from the LLM's response
3. **Executes** the commands in the container via `environment.exec()`
4. **Checks** the result -- if it failed, sends the error back to the LLM
5. **Repeats** until success or max iterations

### self.model_name

The model name is passed via the `-m` CLI flag and available as `self.model_name` on the agent instance. Here it carries a **gateway alias** (`gemma-large`), not a provider model id. The agent accepts either a bare alias or a prefixed form and normalises them:

```python
model = self.model_name or DEFAULT_MODEL          # -m is optional
alias = model.split("/", 1)[1] if "/" in model else model
```

Omit `-m` entirely and the agent falls back to `DEFAULT_MODEL`.

### LiteLLM

LiteLLM provides a unified API for calling any LLM provider. This lesson points it at the local proxy, so the `openai/` prefix means "an OpenAI-compatible endpoint" — the alias after it is resolved to a real provider by the proxy's config:

```python
from litellm import acompletion

response = await acompletion(
    model="openai/gemma-large",
    api_base="http://localhost:4000/v1",   # LITELLM_BASE_URL
    api_key="sk-litellm-master",           # LITELLM_API_KEY
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.0,
)
```

To call a provider directly instead, drop `api_base` and `api_key` and pass a full model string (e.g. `anthropic/claude-sonnet-4-5-20250929`) with that provider's key in the environment. Routing through the proxy is what keeps a provider swap a config change rather than a code change.

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
harbor run -p tasks/llm-task --agent agent:LLMAgent -m gemma-large
```

## Running the Lesson

```bash
# 1. Start the gateway (from the agent-eval-benchmark repo)
cd agent-eval-benchmark/infra && podman compose up -d

# 2. Run the lesson
cd tutorial/level-2-intermediate/module-04-custom-agents/lesson-4-agent-with-llm
uv sync
uv run python main.py
```

`main.py` checks Docker and the gateway before running, and skips the evaluation with a recovery hint if either is missing. Override the endpoint with `LITELLM_BASE_URL` / `LITELLM_API_KEY` if your gateway is not on `http://localhost:4000/v1`.

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

  [OK] Docker is running
  [OK] LiteLLM gateway is reachable at http://localhost:4000

  Running: harbor run -p tasks/llm-task --agent agent:LLMAgent -m gemma-large
  [LLMAgent] Iteration 1/3
  [LLMAgent] Sending request to gemma-large...
  [LLMAgent] All commands succeeded on iteration 1
```

The task is verified by `tests/test.sh`, which runs the generated `/home/user/primes.py` and compares its output to `997`. A successful run scores a reward of **1.0**.

## Key Takeaways

- LLM-powered agents use language models for reasoning about tasks
- The agent-LLM-environment loop: ask LLM -> execute -> check -> retry
- `self.model_name` receives the `-m` flag from the harbor CLI
- The LiteLLM proxy serves the model behind a friendly alias, so switching providers never touches the agent code
- Iterative refinement with error feedback improves success rates

## Next Steps

You have completed **Module 4: Building Custom Agents**!

Next: **Module 5 -- Evaluating Real-World Agents** -- Learn to evaluate Claude Code, Langchain, Langgraph, and more.
