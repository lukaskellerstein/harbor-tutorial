# Parallel Evaluation

**Duration:** 30-45 minutes

## Overview

Running hundreds of evaluation trials sequentially can take hours or days. This lesson teaches you how to use Harbor's concurrency controls to run multiple trials in parallel, dramatically reducing wall-clock time. You will create a 4-task dataset, run it serially and in parallel, and compare the results.

## Prerequisites

- Completed Level 1 and Level 2 of the Harbor Tutorial
- Completed Lesson 1: Cloud Sandbox Environments (recommended)
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running

## Concepts

### Why Parallelism Matters

A typical evaluation trial involves building a container, running the agent, and verifying results. Each trial might take 1-10 minutes. Across a 500-task benchmark, sequential execution could take 8-80+ hours.

With parallelism, you divide that time by the number of concurrent trials:

| Tasks | Time per trial | n=1 (serial) | n=4 | n=32 (cloud) |
|-------|---------------|--------------|-----|--------------|
| 50    | 5 min         | 4.2 hours    | 1 hour | 8 min |
| 500   | 5 min         | 42 hours     | 10.5 hours | 1.3 hours |

### Concurrency Configuration

Harbor's concurrency is controlled by the `n_concurrent_trials` field (top-level in job config) or the `-n` CLI flag. The default is 4.

**Note:** The `orchestrator` config key with `type: local` and nested `n_concurrent_trials` is deprecated. Use top-level `n_concurrent_trials` and `quiet` instead.

### Per-Agent Concurrency

When running multiple agents in the same job, you can set `n_concurrent` on each agent as a sub-limit. This prevents one agent from monopolizing all trial slots.

### Local vs Cloud Parallelism

- **Local Docker**: CPU-bound. Practical limit is 2-8 concurrent trials depending on your machine.
- **Cloud sandboxes**: I/O-bound (waiting for LLM responses). Scale to 32-128+ concurrent trials.

## Step-by-Step

### Step 1: Check Prerequisites

Verify Harbor CLI and Docker are available.

### Step 2: Understand Parallelism

Review the math behind parallel speedup and why it matters at scale.

### Step 3: Concurrency Configuration

Learn the `n_concurrent_trials` field and `-n` CLI flag.

### Step 4: Explore the Dataset

See the 4-task dataset included with this lesson. Each task asks the agent to create a file with specific content.

### Step 5: Generate Job Configs

The lesson generates two job configs:
- `configs/serial.yaml` — runs with `n_concurrent_trials: 1`
- `configs/parallel.yaml` — runs with `n_concurrent_trials: 4`

### Step 6: Run the Comparison

Both configs are executed against the same 4-task dataset using the `oracle` agent. Wall-clock times are measured and compared.

### Step 7: Review Results

See the speedup from parallel execution and learn how cloud environments amplify this benefit.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-10-scaling-cloud/lesson-2-parallel-evaluation
uv sync
uv run python main.py
```

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Level 3, Module 10         #
#          Lesson 2: Parallel Evaluation                #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  [OK] Harbor CLI is installed
  [OK] Docker is running

============================================================
Step 6: Serial vs Parallel — Timing Comparison
============================================================

  Running 4 tasks with the oracle agent...
  First serial (n=1), then parallel (n=4).

  Running: harbor run -c .../serial.yaml
  Mode: Serial (n_concurrent_trials=1)
  --------------------------------------------------
  ...trial output...
  --------------------------------------------------
  Wall-clock time: 45.2 seconds

  Running: harbor run -c .../parallel.yaml
  Mode: Parallel (n_concurrent_trials=4)
  --------------------------------------------------
  ...trial output...
  --------------------------------------------------
  Wall-clock time: 18.7 seconds

============================================================
Step 7: Results Comparison
============================================================

  Serial   (n=1):   45.2 seconds
  Parallel (n=4):   18.7 seconds

  Speedup: 2.4x faster with parallel execution
```

## Key Takeaways

- Use `-n <N>` or `n_concurrent_trials` in job config to control concurrency
- The `orchestrator` config key is deprecated; use top-level fields instead
- Per-agent `n_concurrent` provides sub-limits within the global cap
- Local Docker parallelism is CPU-bound (typically 2-8 concurrent trials)
- Cloud sandboxes are I/O-bound, enabling 32-128+ concurrent trials
- Speedup is most dramatic with longer-running tasks

## Next Steps

Proceed to the next lesson: **network-policies** (controlling network access in evaluation containers).
