# Built-in Agents

**Duration:** 15-20 minutes

## Overview

Survey Harbor's 37+ built-in agents, understand how they are organized by category, and learn the CLI syntax for running evaluations with different agents and models. This lesson is primarily informational, with a short demo using the oracle agent.

## Prerequisites

- Completed Lesson 2: Job Configuration with job.yaml
- Docker installed and running
- Harbor installed (`uv tool install harbor`)
- API keys for LLM providers (optional -- only needed to run real agents)

## Concepts

### Agent Categories

Harbor's built-in agents fall into several categories:

**General-purpose coding agents** -- The largest category. These are full-featured AI coding assistants that can read code, write files, execute commands, and solve programming tasks. Examples: `claude-code`, `codex`, `gemini-cli`, `aider`, `openhands`, `goose`.

**Multi-agent and framework agents** -- Agents built on multi-agent frameworks or specialized reasoning approaches. Examples: `langgraph`, `deerflow`, `dspy-rlm`.

**Specialized SWE agents** -- Agents purpose-built for software engineering tasks, particularly bug fixing and code generation. Examples: `swe-agent`, `mini-swe-agent`.

**Computer-use agents** -- Agents that interact with the environment through screen interaction or terminal commands. Examples: `computer-1`, `terminus-2`.

**Protocol-based agents** -- Agents that connect via the Agent Communication Protocol (ACP). Use with the `acp:` prefix.

**Utility agents** -- Special-purpose agents for task validation. `oracle` runs the reference solution; `nop` does nothing (baseline).

### Model Specification (LiteLLM Format)

Harbor uses LiteLLM model naming: `<provider>/<model-id>`. Examples:
- `anthropic/claude-sonnet-4-5-20250929`
- `anthropic/claude-opus-4-1-20250620`
- `openai/gpt-4o`
- `openai/o3-mini`
- `gemini/gemini-2.5-pro`

The model provider determines which API key is needed (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).

## Step-by-Step

### Step 1: Browse the agent catalog

Run the lesson to see all 37+ agents organized by category with descriptions.

### Step 2: Understand CLI syntax

The basic pattern for running any agent:

```bash
harbor run -p <tasks> -a <agent-name> -m <provider/model> --delete
```

### Step 3: Compare agents in a job

Multiple agents can be evaluated in a single job.yaml:

```yaml
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929
  - name: codex
    model_name: openai/gpt-4o
```

### Step 4: Run a demo trial

The lesson runs a quick trial with the oracle agent to demonstrate the full workflow without requiring API keys.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-03-running-evaluations/lesson-3-builtin-agents
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  Harbor Tutorial - Module 3, Lesson 3
  Built-in Agents
============================================================

------------------------------------------------------------
GENERAL-PURPOSE CODING AGENTS
------------------------------------------------------------
  claude-code            Anthropic's Claude Code CLI agent
  copilot-cli            GitHub Copilot CLI agent
  cursor-cli             Cursor editor CLI agent
  codex                  OpenAI Codex CLI agent
  ...

------------------------------------------------------------
UTILITY AGENTS
------------------------------------------------------------
  oracle                 Runs solution/solve.sh -- validates task correctness
  nop                    Does nothing -- tests environment builds

============================================================
Step 2: Using agents via the CLI
============================================================
  # Anthropic Claude Sonnet
  harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-4-5-20250929 --delete

  # OpenAI GPT-4o
  harbor run -p tasks -a codex -m openai/gpt-4o --delete
  ...

============================================================
Step 4: Demo -- running with the oracle agent
============================================================
Running...
Trial completed!
```

## Key Takeaways

- Harbor has 37+ built-in agents spanning general-purpose, framework, SWE, computer-use, and utility categories
- Use `-a <agent-name>` to select a built-in agent by name
- Use `-m <provider>/<model>` to specify the model in LiteLLM format
- Multiple agents and models can be compared in a single job
- Custom agents can also be used via import paths: `-a module.path:ClassName`

## Next Steps

Proceed to [Oracle & Nop Agents](../lesson-4-utility-agents/) to learn how to use utility agents for systematic task validation.
