# Running SWE-Bench

**Duration:** 30 minutes (read and understand) + optional 30-60 minutes (running)

## Overview

SWE-bench is the definitive benchmark for evaluating AI coding agents on real-world software engineering tasks. Each instance is a real GitHub issue from a popular Python project, complete with the repository, failing tests, and the developer's original patch. This lesson explains how Harbor's SWE-bench adapter works and walks you through configuring and running an evaluation. Because SWE-bench evaluations are expensive (real API calls, minutes per trial), this lesson is designed as "read and understand" with an optional hands-on run.

## Prerequisites

- Completed Lesson 1: What Are Adapters?
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running
- `ANTHROPIC_API_KEY` environment variable set (for optional run)
- Budget awareness: each trial costs $0.05-$2.00 in API calls

## Concepts

### What Is SWE-bench?

SWE-bench (Software Engineering Benchmark) was created by researchers at Princeton and evaluates AI agents on their ability to resolve real GitHub issues. Each instance consists of:

- A **problem statement** (the original GitHub issue text)
- A **repository snapshot** (the code at the commit before the fix)
- A **test patch** (new tests the developer wrote to verify the fix)
- A **ground truth patch** (the developer's actual fix)

The repositories include Django, Flask, scikit-learn, matplotlib, sympy, requests, pytest, astropy, sphinx, and more.

**SWE-bench Verified** is a curated subset of 500 human-validated instances chosen for clear problem statements and reliable test suites.

### How the Adapter Works

The SWE-bench adapter converts each HuggingFace dataset instance into a Harbor task:

| HuggingFace Field | Harbor File | Purpose |
|---|---|---|
| `problem_statement` | `instruction.md` | What the agent must fix |
| `repo` + `base_commit` | `Dockerfile` | Checkout the repo at the right commit |
| `test_patch` | `test.sh` | Apply test patch and run test suite |
| `patch` | `solve.sh` | Reference solution (oracle) |
| Instance metadata | `task.toml` | Configuration and metadata |

### Cost and Time

SWE-bench evaluations are resource-intensive. A full 500-task run with Claude Code can cost $25-$500+ in API calls and take hours even with parallelism. Always start with a single task or small subset.

## Step-by-Step

### Step 1: Check Prerequisites

The lesson verifies that Harbor and Docker are available. Both are required to run SWE-bench evaluations.

### Step 2: Understand SWE-bench

Learn what SWE-bench evaluates and why it matters for coding agent development.

### Step 3: Understand the Adapter Flow

See how each HuggingFace dataset field maps to a Harbor task file.

### Step 4: Study the Job Configuration

Examine `swe-bench-job.yaml` and understand each configuration field: jobs_dir, n_attempts, orchestrator, environment, agents, and datasets.

### Step 5: Learn the CLI Commands

See the exact commands for running full evaluations, single instances, and cloud-parallel runs.

### Step 6: Understand Cost Implications

Review time and cost estimates to plan your evaluation budget.

### Step 7: Understand Results

Learn the results directory structure and how to view outcomes with `harbor view jobs`.

### Step 8: (Optional) Run a Single Task

If prerequisites are met and you are comfortable with the cost, try running a single SWE-bench task.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-09-adapters/lesson-2-swe-bench-adapter
uv sync
uv run python main.py
```

To optionally run a SWE-bench evaluation (costs real API credits):

```bash
# Single task from the mini dataset
harbor run -d harbor-framework/swe-bench-verified-mini \
           -a claude-code \
           -m anthropic/claude-sonnet-4-5-20250929 \
           -n 1

# Or use the included job config
harbor run -c swe-bench-job.yaml
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Level 3, Module 9          #
#          Lesson 2: Running SWE-Bench                  #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================

  [OK] Harbor CLI is installed
  [OK] Docker is running

============================================================
Step 2: What Is SWE-Bench?
============================================================

SWE-bench (Software Engineering Benchmark) evaluates AI agents
on real GitHub issues from popular open-source Python projects.
...

============================================================
Step 4: SWE-Bench Job Configuration
============================================================

File: swe-bench-job.yaml

jobs_dir: jobs
n_attempts: 1
...

============================================================
Step 6: Cost and Time Considerations
============================================================

  Per Trial:
    - Docker image build:  1-5 minutes
    - Agent execution:     2-30 minutes
    ...

============================================================
Summary
============================================================

Key takeaways:
  1. SWE-bench evaluates agents on real GitHub issues
  ...
```

## Key Takeaways

- SWE-bench is the most widely used benchmark for coding agent evaluation
- The adapter converts HuggingFace dataset instances into Harbor task directories
- Configure evaluations with a job.yaml file for reproducibility
- Always start with a single task (`-n 1`) or mini dataset before scaling up
- Full evaluations are expensive — budget $25-$500+ for 500 tasks
- Results include rewards, agent trajectories, and detailed test output

## Next Steps

Proceed to the next lesson: **custom-adapter** — Building a Custom Adapter from scratch to convert your own benchmark data into Harbor tasks.
