# Evaluating Claude Code

**Duration:** 30-45 minutes

## Overview

Claude Code is one of Harbor's built-in agents. Unlike the custom agents you built in Module 4, built-in agents require no wrapper code -- you simply reference them by name. In this lesson, you will run Claude Code against custom tasks and learn how to analyze its performance through results and trajectories.

## Prerequisites

- Completed Module 4 (Building Custom Agents)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- Anthropic credentials in this lesson's `.env` file (see Authentication below)

## Authentication

This lesson bills your **Claude Pro/Max subscription** rather than the pay-per-token API. Generate a long-lived subscription token once:

```bash
claude setup-token   # opens a browser; prints a token valid for one year
```

Then put it in a `.env` file in this lesson directory (git-ignored):

```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

`main.py` loads this file with `python-dotenv` at startup and passes it to `harbor run`, along with `CLAUDE_FORCE_OAUTH=1` — Harbor's switch that drops any API key so the CLI bills the subscription.

Using an API key instead is still supported: put `export ANTHROPIC_API_KEY=sk-ant-...` in `.env` and omit the OAuth token.

> **Running `harbor run -c job.yaml` directly?** The `.env` file is only loaded by `main.py`. For a direct CLI run, source it into your shell first: `source .env && export CLAUDE_FORCE_OAUTH=1`. (The `export` prefixes in `.env` exist so this works.)

## Concepts

### Built-in Agents

Harbor ships with 37+ built-in agents including `claude-code`, `openhands`, `aider`, `codex`, and many more. These agents are pre-configured to work with Harbor's evaluation pipeline. You reference them by name:

```bash
harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-4-5-20250929
```

### How Claude Code Works in Harbor

When Harbor runs the `claude-code` agent:

1. **Container setup** -- Harbor builds a Docker container from the task's Dockerfile
2. **Agent installation** -- Claude Code is installed inside the container automatically
3. **Execution** -- The agent receives the instruction and uses its tools (Bash, Read, Edit, etc.) to complete the task
4. **Verification** -- Harbor runs the test script and records the reward (0-1)

### Environment Variables

Claude Code runs *inside* the container, so it needs credentials there -- but you do **not** put them in `job.yaml` or bake them into the image (that would persist the secret in the image layers).

Harbor's built-in `claude-code` agent reads `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) from the host environment and injects it into the container's environment at the moment it invokes the CLI. That is why `job.yaml` here has no `environment.env` block at all:

```yaml
environment:
  type: docker
  force_build: true
  delete: true
```

The credential chain is: `.env` -> `main.py` (`load_dotenv`) -> `harbor run` subprocess -> container environment.

## Step-by-Step

### Step 1: Examine the Tasks

This lesson includes two tasks of varying difficulty:

- **hello-task** -- Create a file with specific content (easy)
- **sort-list** -- Write and run a Python sorting script (easy-medium)

Each task follows the standard Harbor task format with `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/test.sh`, and `solution/solve.sh`.

### Step 2: Review the Job Configuration

The `job.yaml` configures the evaluation:

```yaml
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929
datasets:
  - path: tasks
```

Key settings:
- `name: claude-code` -- uses the built-in agent
- `model_name` -- specifies the Claude model (LiteLLM format: `provider/model`)
- `n_concurrent_trials: 1` -- runs one trial at a time

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-1-claude-code-eval
uv sync
# credentials come from .env -- see Authentication above
uv run python main.py
```

### Step 4: Inspect Results

After the evaluation, results are stored in `jobs/`. Each trial directory contains:

- `config.json` -- trial configuration
- `result.json` -- reward, duration, and metadata
- `logs/agent/` -- agent trajectory (every tool call Claude Code made)
- `logs/verifier/` -- verifier output and reward

Use `harbor view jobs` to explore results interactively in a web UI.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-1-claude-code-eval
uv sync
# credentials come from .env -- see Authentication above
uv run python main.py
```

## Expected Output

```
Step 1: Checking Prerequisites
  [OK] Docker is running
  [OK] Harbor CLI is installed
  [OK] CLAUDE_CODE_OAUTH_TOKEN loaded (Claude subscription auth)

Step 2: Understanding the Built-in Claude Code Agent
  Claude Code is one of Harbor's 37+ built-in agents.
  ...

Step 4: Running Evaluation with Claude Code
  Running: harbor run -c job.yaml
  ...

Step 5: Inspecting Results and Trajectories
  Task: tutorial/hello-task
    Reward: 1.0
  Task: tutorial/sort-list
    Reward: 1.0
  Average reward: 1.00
  Tasks passed: 2/2
```

## Key Takeaways

- Claude Code is a built-in Harbor agent -- no custom wrapping code needed
- Use `job.yaml` to configure evaluations with agents, models, and datasets
- The `claude-code` agent injects host credentials into the container itself -- no `environment.env` entry and no secret in the image
- A `claude setup-token` OAuth token bills your Claude subscription instead of the API
- Results include rewards, duration, and full agent trajectories
- Use `harbor view jobs` to explore results interactively

## Next Steps

In the next lesson, you will learn how to wrap a Langchain agent as a Harbor `BaseAgent`, bridging two different agent frameworks.
