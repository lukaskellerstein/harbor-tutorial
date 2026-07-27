# Agent Trajectories

**Duration:** 30-40 minutes

## Overview

Agent trajectories are the complete execution traces of every action an agent takes during a trial -- every LLM call, tool invocation, command output, and observation. Understanding trajectories is essential for debugging failures, optimizing agent behavior, and comparing how different agents approach the same task. This lesson teaches you how to generate, inspect, and export trajectory data using Harbor.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### What Is a Trajectory?

When an agent attempts a task inside Harbor, every step it takes is recorded: the instructions it receives, the commands it runs, the outputs it observes, and the decisions it makes. This ordered sequence of steps is the agent's **trajectory**.

Trajectories are stored in ATIF (Agent Trajectory Interchange Format) v1.7, a standardized JSON schema that works across all agents and environments. The format captures:

- **Steps** -- each action or observation in order
- **Tool calls** -- commands the agent executed in the environment
- **Observations** -- outputs and results the agent received
- **Metrics** -- token counts, cost, and timing data

### Trial Output Structure

Each trial produces a directory containing:

```
trial-<id>/
  agent/              -- Agent logs and trajectory (trajectory.json)
  verifier/           -- Test output (test-stdout.txt, test-stderr.txt, reward.txt)
  artifacts/          -- Collected artifacts from the environment
  config.json         -- Trial configuration for reproducibility
  result.json         -- Trial results (reward, timing, agent info)
  trial.log           -- Execution log
```

The `result.json` file contains the trial outcome, including `verifier_result.rewards` which holds the reward score (0 to 1). The `agent/trajectory.json` file contains the full ATIF trajectory.

### ATIF v1.7 Schema

The top-level trajectory object contains:

- `version` -- ATIF version string
- `metadata` -- agent name, model, task info
- `steps[]` -- ordered list of step objects, each with:
  - `step_id` -- unique identifier
  - `timestamp` -- ISO 8601 timestamp
  - `source` -- "system", "user", or "agent"
  - `message` -- text content
  - `tool_calls[]` -- tools invoked (name, input)
  - `observation` -- result of tool execution
  - `metrics` -- token counts, cost, latency

## Step-by-Step

### Step 1: What Are Agent Trajectories?

The lesson begins by explaining what trajectories capture and why they matter. Trajectories are essential for four purposes: debugging agent failures, optimizing behavior by finding wasted steps, comparing different agents on the same task, and ensuring reproducibility.

### Step 2: Running a Trial

We run a trial using the `oracle` agent against a multi-step task that creates three files. The oracle agent executes the reference solution (`solution/solve.sh`), which gives us a known-good trajectory to inspect.

```bash
harbor trial start -p tasks/trace-task -a oracle --delete --trials-dir trials
```

### Step 3: Inspecting Trial Output

After the trial completes, we walk through the output directory structure. Key files to examine:

- `result.json` -- contains the reward score and timing information
- `verifier/reward.txt` -- the raw reward value written by the test script
- `verifier/test-stdout.txt` -- test script output showing pass/fail details
- `agent/trajectory.json` -- the full ATIF trajectory

### Step 4: Understanding ATIF Format

We examine the ATIF v1.7 schema in detail, showing how each step in the trajectory maps to an agent action. The formatted example shows the structure of a trajectory with system prompts, agent actions, tool calls, and observations.

### Step 5: Viewing and Exporting Trajectories

Harbor provides two ways to work with trajectories after they are recorded:

**Web viewer:**
```bash
harbor view trials/
```
Launches an interactive web UI that renders trajectories as a timeline with expandable steps.

**Export for analysis:**
```bash
harbor traces export -p trials/
```
Extracts trajectories into formats suitable for analysis or fine-tuning. Key flags include `--filter` (success/failure/all), `--sharegpt` (ShareGPT format), and `--subagents` (include sub-agent traces).

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-10-analysis-optimization/lesson-2-trajectories
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  HARBOR TUTORIAL
  Level 3 | Module 10 | Lesson 2: Agent Trajectories
============================================================

============================================================
PREREQUISITES CHECK
============================================================
[OK] Docker is running
[OK] Harbor CLI is available

============================================================
STEP 1: What Are Agent Trajectories?
============================================================
An agent trajectory is the complete execution trace of every
action an agent takes during a trial...

============================================================
STEP 2: Running a Trial to Generate a Trajectory
============================================================
Running: harbor trial start -p tasks/trace-task -a oracle --delete --trials-dir trials
...trial output...

============================================================
STEP 3: Inspecting Trial Output Structure
============================================================
A trial directory contains everything about one agent attempt:
  agent/          <- Agent logs and trajectory (trajectory.json)
  verifier/       <- Test output (test-stdout.txt, test-stderr.txt, reward.txt)
  config.json     <- Trial configuration for reproducibility
  result.json     <- Trial results (reward, timing, agent info)
  ...

  Reward: {'reward': 1.0}

============================================================
STEP 4: Understanding ATIF (Agent Trajectory Interchange Format)
============================================================
ATIF v1.7 is Harbor's standardized schema for recording agent
trajectories...

============================================================
STEP 5: Viewing and Exporting Trajectories
============================================================
  harbor view trials/
  harbor traces export -p trials/

============================================================
RECAP
============================================================
  1. Agent trajectories capture the complete execution trace...
  2. Trial output is organized into agent/, verifier/, artifacts/...
  3. ATIF v1.7 is Harbor's standardized schema...
  4. `harbor view <folder>` launches a web UI...
  5. `harbor traces export` extracts trajectories...
```

## Key Takeaways

- Agent trajectories record every action, tool call, and observation during a trial, giving you full visibility into agent behavior.
- Trial output directories follow a consistent structure: `agent/`, `verifier/`, `artifacts/`, `config.json`, `result.json`, and `trial.log`.
- ATIF v1.7 (Agent Trajectory Interchange Format) is the standardized schema that makes trajectories comparable across agents and environments.
- `harbor view <folder>` launches an interactive web UI for exploring trajectories visually.
- `harbor traces export -p <path>` extracts trajectories for external analysis, fine-tuning, or sharing, with filters for outcome, format, and sub-agents.

## Next Steps

Continue to the **Sweeps** lesson to learn how to systematically vary parameters and find optimal agent configurations.
