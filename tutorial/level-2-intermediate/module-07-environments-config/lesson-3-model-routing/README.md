# Model Selection & LiteLLM

**Duration:** 20-30 minutes

## Overview

Harbor uses the LiteLLM naming convention (`provider/model-name`) to route model requests to the correct API. This lesson explains the model format, shows how to configure models on the CLI and in `job.yaml`, and demonstrates how to use local models through LMStudio.

## Prerequisites

- Completed Level 1 (Modules 1-3)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- (Optional) LMStudio installed for local model serving
- (Optional) API key for Anthropic or OpenAI for cloud model testing

## Concepts

### LiteLLM Model Format

Harbor uses the `provider/model-name` convention from LiteLLM. The provider prefix determines which API endpoint receives the request:

| Provider | Example | API Endpoint |
|----------|---------|-------------|
| `anthropic/` | `anthropic/claude-sonnet-4-5-20250929` | Anthropic Messages API |
| `anthropic/` | `anthropic/claude-opus-4-1` | Anthropic Messages API |
| `openai/` | `openai/gpt-4o` | OpenAI Chat API |
| `openai/` | `openai/gpt-4o-mini` | OpenAI Chat API |
| `openai/` | `openai/gemma4-e4b` | Any OpenAI-compatible API (e.g., LMStudio) |

The `openai/` prefix is special: by overriding `OPENAI_BASE_URL`, you can route to any OpenAI-compatible server, including local inference engines like LMStudio, Ollama, or vLLM.

### LMStudio for Local Models

LMStudio serves local models via an OpenAI-compatible API at `http://localhost:1234/v1`. Because Harbor tasks run inside Docker containers, you use `host.docker.internal` to reach the host machine:

```
http://host.docker.internal:1234/v1
```

### The --agent-env Flag

The `--agent-env` CLI flag passes environment variables into the agent's execution context. This is how you provide API keys, override endpoints, and pass other configuration:

```bash
harbor run -p tasks/model-test -a claude-code \
    -m openai/gemma4-e4b \
    --agent-env OPENAI_BASE_URL=http://host.docker.internal:1234/v1 \
    --agent-env OPENAI_API_KEY=lm-studio
```

## Step-by-Step

### Step 1: Understand the LiteLLM Model Format

The `provider/model-name` convention tells Harbor two things: (1) which client library to use and (2) which model to request. For example, `anthropic/claude-sonnet-4-5-20250929` uses the Anthropic client to request the Claude Sonnet model.

### Step 2: Use the -m Flag on the CLI

```bash
# Anthropic model
harbor run -p tasks/model-test -a claude-code \
    -m anthropic/claude-sonnet-4-5-20250929

# OpenAI model
harbor run -p tasks/model-test -a claude-code \
    -m openai/gpt-4o
```

### Step 3: Configure Models in job.yaml

For multi-model comparisons, define each agent+model combination in `job.yaml`:

```yaml
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929

  - name: claude-code
    model_name: openai/gpt-4o
```

Each entry creates a separate trial, letting you compare performance across models.

### Step 4: Set Up LMStudio (Optional)

1. Install LMStudio from https://lmstudio.ai
2. Download a model (recommended: Gemma4-E4B)
3. Start the server: `lms server start`
4. Run with Harbor:

```bash
harbor run -p tasks/model-test -a claude-code \
    -m openai/gemma4-e4b \
    --agent-env OPENAI_BASE_URL=http://host.docker.internal:1234/v1 \
    --agent-env OPENAI_API_KEY=lm-studio
```

### Step 5: Validate the Test Task

The lesson runs the included task with the oracle agent to verify the task definition works before you try it with real models.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-07-environments-config/lesson-3-model-routing
uv sync
uv run python main.py
```

## Expected Output

```
Step 1: LiteLLM Model Format

  Provider Examples:
  ----------------------------------------------------------
  Provider     Model Name                            API
  ----------------------------------------------------------
  anthropic/   claude-sonnet-4-5-20250929             Anthropic
  openai/      gpt-4o                                 OpenAI
  openai/      gemma4-e4b          Local (LMStudio)   *
  ----------------------------------------------------------

...

Step 4: Local Models with LMStudio

  LMStudio CLI not found on this system.
  Install from https://lmstudio.ai to use local models.

...

Step 6: Validating the Test Task
  [OK] Task validated successfully
```

## Key Takeaways

- Harbor uses LiteLLM's `provider/model-name` format for model selection
- The `-m` flag on the CLI specifies the model: `-m anthropic/claude-sonnet-4-5-20250929`
- Use `job.yaml` to define multi-model comparison runs
- The `openai/` prefix with a custom `OPENAI_BASE_URL` routes to any OpenAI-compatible API
- LMStudio serves local models at `localhost:1234/v1`; use `host.docker.internal` from containers
- The `--agent-env` flag passes environment variables (API keys, endpoints) into the agent

## Next Steps

Continue to Module 8 -- Adapters, to learn how to convert external benchmarks (like SWE-Bench) into Harbor task format.
