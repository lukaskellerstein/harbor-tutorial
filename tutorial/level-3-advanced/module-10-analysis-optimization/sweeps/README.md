# Configuration Sweeps

**Duration:** 35-45 minutes

## Overview

Configuration sweeps let you systematically and iteratively evaluate agents across a set of tasks. After each sweep round, tasks that succeed are dropped, focusing all remaining compute on the hardest unsolved problems. This lesson teaches you how to use `harbor sweeps run` to run multi-round evaluations and use the hint system to guide agents on difficult tasks.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Completed Module 10 Lessons 1-2 (metrics, trajectories)
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### What Is a Sweep?

A sweep is an iterative evaluation strategy. Instead of running every task once, you run multiple rounds:

1. **Round 1** -- Run all tasks in the dataset
2. Tasks with reward > 0 are marked as "solved" and removed from the pool
3. **Round 2** -- Run only the remaining (failed) tasks
4. Again, newly solved tasks are removed
5. **Round 3** -- Continue with the stubbornest failures
6. Stop when `--max-sweeps` is reached or all tasks pass

This is valuable because:
- Some tasks are **flaky** -- they may pass on retry due to non-determinism
- You can add **hints** in later rounds to help agents with hard tasks
- You **save compute** by not re-running tasks that already passed

### The Hint System

Sweeps support two hint mechanisms:

- **Generic hint** (`--hint "..."`) -- A single hint string added to every agent's kwargs. Good when all tasks share a common strategy.
- **Per-task hints** (`--hints-file hints.json`) -- A JSON object mapping task names to individual hint strings. When provided, each task gets its own job so it receives only its specific hint. This is ideal for giving targeted guidance on the hardest tasks.

### Sweep Configuration

The sweep config is a standard Harbor `JobConfig` (same format as `job.yaml`). The `harbor sweeps run` command layers sweep-specific behavior on top: iterative rounds, task filtering, and hint injection.

## Step-by-Step

### Step 1: What Are Configuration Sweeps?

Sweeps solve a common evaluation problem: when you have a large benchmark, some tasks may fail due to randomness rather than fundamental inability. Running every task again wastes compute on tasks the agent already solved. Sweeps automate the "re-run only failures" pattern.

### Step 2: Sweep Configuration

The `sweep-config.yaml` in this lesson is a standard JobConfig:

```yaml
datasets:
  - path: tasks

agents:
  - name: oracle

environment:
  type: docker
  delete: true

orchestrator:
  type: local
  n_concurrent_trials: 2
```

We use the `oracle` agent (which runs `solution/solve.sh`) to validate our tasks. In a real evaluation, you would use an actual AI agent.

### Step 3: Running a Sweep

The `harbor sweeps run` command accepts these flags:

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --config` | (required) | Job config file (YAML or JSON) |
| `--max-sweeps` | 3 | Maximum number of sweep rounds |
| `--trials-per-task` | 2 | Trials per task per sweep round |
| `--hint` | None | Generic hint string for all agents |
| `--hints-file` | None | JSON file mapping task names to hints |

Example command:

```bash
harbor sweeps run -c sweep-config.yaml --max-sweeps 2 --trials-per-task 1
```

### Step 4: Understanding Sweep Results

After each round, the sweep command reports:
- How many tasks were in the pool
- How many succeeded (reward > 0)
- How many remain for the next round

Results are stored in the standard `jobs/` directory. Each sweep round creates a separate job directory with `result.json` files for each trial.

### Step 5: Using Hints

For hard tasks that consistently fail, you can provide hints:

**Generic hint** (same hint for all tasks):
```bash
harbor sweeps run -c config.yaml --hint "Focus on edge cases and error handling"
```

**Per-task hints** (targeted guidance):
```bash
harbor sweeps run -c config.yaml --hints-file hints.json
```

Where `hints.json` contains:
```json
{
  "tutorial/sweeps-reverse-string": "Use Python slicing [::-1]",
  "tutorial/sweeps-fibonacci": "Start with a=0, b=1 and iterate",
  "tutorial/sweeps-json-transform": "Use json.load, list comprehension, and sorted()"
}
```

When `--hints-file` is provided, each task runs as its own individual job so that each agent receives only its task-specific hint in its kwargs.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-10-analysis-optimization/sweeps
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  Harbor Tutorial
  Module 10, Lesson 3: Configuration Sweeps
============================================================

============================================================
Step 0: Checking Prerequisites
============================================================
  [OK] Docker is installed and running.
  [OK] Harbor is installed.

============================================================
Step 1: What Are Configuration Sweeps?
============================================================

Configuration sweeps provide systematic, iterative exploration of
agent/model/config combinations across a set of tasks.
...

============================================================
Step 4: Running a Sweep
============================================================

Command: harbor sweeps run -c sweep-config.yaml --max-sweeps 2 --trials-per-task 1

Running sweep (this may take a minute or two)...
----------------------------------------
  [sweeps] Starting sweep 1 with 3 tasks, 1 trials/task
  [sweeps] Sweep 1 complete. Tasks: 3 -> 0 remaining
  [sweeps] All tasks succeeded; stopping early.
  [sweeps] Skipping push; set --push and --export-repo to upload.
----------------------------------------
Sweep completed successfully.

============================================================
Step 5: Understanding Sweep Results
============================================================

Found 1 job directory(ies) from the sweep:
  - <job-id>

--- Sweep Round 1: <job-id> ---
  Task: tutorial/sweeps-reverse-string       Reward: 1.0  [PASS]
  Task: tutorial/sweeps-fibonacci             Reward: 1.0  [PASS]
  Task: tutorial/sweeps-json-transform        Reward: 1.0  [PASS]
...

============================================================
Recap
============================================================

In this lesson you learned:

  1. SWEEPS are iterative evaluation rounds that drop successful
     tasks after each round, focusing compute on failures.
  ...
```

## Key Takeaways

- Sweeps automate the "re-run only failures" pattern, saving compute on large benchmarks.
- The `harbor sweeps run` command wraps a standard JobConfig with iterative round logic.
- After each round, tasks with any trial achieving reward > 0 are dropped from future rounds.
- The `--hint` flag provides a generic hint to all agents; `--hints-file` gives per-task targeted hints.
- Sweeps are especially powerful when combined with hints: run without hints first, then add targeted guidance for the hardest remaining tasks.

## Next Steps

Continue to the **analyze-check** lesson to learn how to use `harbor analyze` and `harbor check` to validate task quality with LLM-powered analysis.
