# Job Configuration with job.yaml

**Duration:** 20-25 minutes

## Overview

Learn how to configure multi-trial evaluation jobs using `job.yaml`. You will understand each section of the configuration file, run a job across multiple tasks, and see how CLI flags can override job settings.

## Prerequisites

- Completed Lesson 1: Running a Single Trial
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### What is a Job?

A **job** is a collection of trials. When you run a job, Harbor creates one trial for every combination of (agent, task) in the configuration. Jobs support:

- Multiple tasks (via a dataset path)
- Multiple agents and models
- Concurrent execution
- Multiple attempts per trial (for pass@k metrics)
- Centralized result collection

### The job.yaml File

A `job.yaml` file is the recommended way to configure reproducible evaluations. It specifies:

- **`jobs_dir`** -- where to store results (default: `./jobs/`)
- **`n_attempts`** -- how many times to attempt each trial
- **`orchestrator`** -- how to manage trial execution (local, concurrent)
- **`environment`** -- container runtime settings (Docker, force rebuild, cleanup)
- **`agents`** -- which agent(s) to evaluate and their models
- **`datasets`** -- which task directories to evaluate against

### Dataset Discovery

When you point `datasets.path` at a directory, Harbor automatically discovers all valid task directories inside it. A valid task must have at minimum `instruction.md` and `task.toml`.

## Step-by-Step

### Step 1: Review the job.yaml

The lesson includes a pre-built `job.yaml`:

```yaml
jobs_dir: jobs
n_attempts: 1

orchestrator:
  type: local
  n_concurrent_trials: 2

environment:
  type: docker
  force_build: true
  delete: true

agents:
  - name: oracle

datasets:
  - path: tasks
```

### Step 2: Understand the dataset

The `tasks/` directory contains two tasks:
- `hello-task` -- create a file with specific content
- `reverse-string` -- write a Python script that reverses strings

### Step 3: Run the job

```bash
harbor run -c job.yaml -y
```

Harbor discovers both tasks, creates a trial for each, and runs them with up to 2 concurrent trials.

### Step 4: Inspect the results

Results are stored in `jobs/<timestamp>/` with one subdirectory per trial. Each trial has `result.json` with rewards and metadata. The job-level `result.json` has aggregate statistics.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-03-running-evaluations/lesson-2-job-config
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  Harbor Tutorial - Module 3, Lesson 2
  Job Configuration with job.yaml
============================================================

============================================================
Step 1: Understanding job.yaml
============================================================
--- job.yaml ---
jobs_dir: jobs
n_attempts: 1
...

Section-by-section breakdown:
  jobs_dir: jobs
    -> Where job results are stored
  orchestrator.n_concurrent_trials: 2
    -> How many trials run in parallel
...

============================================================
Step 3: Running the job with `harbor run -c job.yaml`
============================================================
Running job...
...
Job completed!
  hello-task:       Reward: 1.0   Status: PASS
  reverse-string:   Reward: 1.0   Status: PASS
```

## Key Takeaways

- `job.yaml` provides reproducible, version-controlled evaluation configuration
- Harbor discovers all tasks in a dataset path automatically
- Each section controls a different aspect: agents, environment, orchestration, datasets
- `harbor run -c job.yaml` is the primary way to run multi-trial evaluations
- CLI flags (`-a`, `-m`, `-n`, `-p`, etc.) can override or substitute for job.yaml settings
- Results are organized in `jobs/<timestamp>/<trial-name>/` with per-trial and aggregate data

## Next Steps

Proceed to [Built-in Agents](../lesson-3-builtin-agents/) to learn about Harbor's 37+ built-in agents and how to evaluate with them.
