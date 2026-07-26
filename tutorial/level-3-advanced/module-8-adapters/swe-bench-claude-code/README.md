# Benchmarking Claude Code on SWE-bench

**Duration:** 30–60 minutes (depends on number of tasks)

## Overview

This lesson runs an end-to-end SWE-bench evaluation using Harbor's built-in `claude-code` agent. You'll configure the benchmark, run it against real GitHub issues, and analyze the results. Unlike the previous SWE-bench adapter lesson (which was conceptual), this one actually executes the benchmark.

## Prerequisites

- Completed: Module 8 Lesson 1 (adapter-intro) and Lesson 2 (swe-bench-adapter)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- `ANTHROPIC_API_KEY` environment variable set
- Budget: ~$1–5 for the mini subset, ~$50–500 for the full benchmark

## Concepts

### SWE-bench as an Agent Benchmark

SWE-bench evaluates AI agents on real software engineering tasks — actual GitHub issues from popular open-source Python projects. Each task gives the agent:

1. A **repository checkout** at the commit before the fix was merged
2. The **issue description** (what's broken or needed)
3. A **test suite** that validates whether the fix is correct

The agent must explore the codebase, understand the problem, and write a patch that passes the tests — exactly what a human developer would do.

### Why Claude Code?

Claude Code is one of the strongest coding agents available. It comes built into Harbor as a registered agent (`-a claude-code`), so no wrapper code is needed. It uses its built-in tools (Bash, Read, Edit, Write) to navigate repos and write patches.

### Dataset Sizes

| Dataset | Tasks | Estimated Cost | Estimated Time (sequential) |
|---------|-------|---------------|----------------------------|
| `swe-bench-verified-mini` | ~20 | $1–5 | 30–60 min |
| `swe-bench-verified` | 500 | $50–500 | 10–50 hours |

### Scaling Strategy

1. **Start small**: Run `swe-bench-verified-mini` locally with `-n 1`
2. **Scale locally**: Run the full set with `-n 8` (8 parallel trials)
3. **Scale to cloud**: Use Daytona/Modal with `-n 32` for maximum speed

## Step-by-Step

### Step 1: Verify Prerequisites

The script checks for Docker, Harbor CLI, and `ANTHROPIC_API_KEY`. All three are required — SWE-bench tasks run in Docker containers, and Claude Code needs an API key.

### Step 2: Understand the Job Configs

Three job configs are provided, each for a different scale:

**swe-bench-job.yaml** — Quick test run:
```yaml
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929
datasets:
  - name: harbor-framework/swe-bench-verified-mini
```

**swe-bench-full.yaml** — Full benchmark, local:
```yaml
n_concurrent_trials: 8
datasets:
  - name: harbor-framework/swe-bench-verified
```

**swe-bench-cloud.yaml** — Full benchmark, cloud:
```yaml
n_concurrent_trials: 32
environment:
  type: daytona
datasets:
  - name: harbor-framework/swe-bench-verified
```

### Step 3: Run the Benchmark

The script runs `harbor run -c swe-bench-job.yaml`, which:

1. Downloads the `swe-bench-verified-mini` dataset
2. For each task instance:
   - Builds a Docker image with the repo checked out at the right commit
   - Installs Claude Code inside the container
   - Passes the issue description as the instruction
   - Lets Claude Code explore, reason, and write a patch
   - Runs the project's test suite to verify the fix
   - Records reward (1.0 = pass, 0.0 = fail)

### Step 4: Analyze Results

The script parses `result.json` from each trial and displays:

- Per-instance pass/fail status
- Duration per task
- Aggregate pass rate and mean reward

### Step 5: Deeper Inspection

After the run, you can:
- Browse results in the web viewer: `harbor view jobs`
- Inspect agent trajectories (every tool call Claude Code made)
- Run LLM-powered analysis: `harbor analyze jobs/<job-id>`
- Compare against other agents by swapping the `agents` section

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-8-adapters/swe-bench-claude-code
export ANTHROPIC_API_KEY=sk-ant-...
uv sync
uv run python main.py
```

## Expected Output

```
Step 1: Checking Prerequisites
  [OK] Docker is running
  [OK] Harbor CLI installed
  [OK] ANTHROPIC_API_KEY is set

Step 2: What We're Running
  Benchmark:  SWE-bench Verified (mini subset)
  Agent:      claude-code (built-in Harbor agent)
  ...

Step 4: Running the Benchmark
  Running: harbor run -c swe-bench-job.yaml
  ...

Step 5: Analyzing Results
  Instance                                       Reward   Duration
  ─────────────────────────────────────────────  ─────── ──────────
  django__django-12345                              PASS     182.3s
  flask__flask-6789                                 FAIL     245.1s
  ...
  TOTAL                                            3/  5     856.2s

  Pass rate:      3/5 (60.0%)
  Mean reward:    0.600
  Total duration: 856s (14.3 min)
```

## Key Takeaways

- SWE-bench + Claude Code is a single command: `harbor run -c swe-bench-job.yaml`
- The mini subset is ideal for testing and iteration (~$1–5)
- Scale from mini → full → cloud as confidence grows
- Compare agents by changing the `agents` section in the job config
- Use `harbor view` and `harbor analyze` to understand agent behavior

## Next Steps

- Try swapping in other agents (aider, openhands, codex) for comparison
- Scale to the full benchmark with `swe-bench-full.yaml`
- Build your own benchmark adapter in the next lesson: [custom-adapter](../custom-adapter/)
