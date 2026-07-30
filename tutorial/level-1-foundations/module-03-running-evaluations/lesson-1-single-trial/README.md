# Running a Single Trial

**Duration:** 15-20 minutes

## Overview

Learn how to run a single agent attempt at a task using `harbor trial start`. You will execute a trial, inspect its output files, and understand how single trials differ from multi-trial jobs.

## Prerequisites

- Completed Module 2: Working with Tasks
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### What is a Trial?

A **trial** is a single agent attempt at a single task. It is the atomic unit of evaluation in Harbor. When you run a trial, Harbor:

1. Builds the Docker container from the task's `environment/Dockerfile`
2. Runs the agent inside the container with the task's `instruction.md`
3. Runs the verifier (`tests/test.sh`) to score the agent's work
4. Stores all results (reward, logs, metadata) in a trial directory

### Trial vs. Job

Harbor provides two commands for running evaluations:

- **`harbor trial start`** -- Runs one trial (one agent, one task). Results go to `./trials/`. Best for testing, debugging, and quick validation.
- **`harbor run`** -- Runs a job (multiple trials). Supports multiple tasks, agents, models, concurrency, and retries. Results go to `./jobs/`. Best for systematic evaluations.

## Step-by-Step

### Step 1: Understand the task

The lesson includes a simple "hello-task" in `tasks/hello-task/`. The agent must create a file containing "Hello, Harbor!" and the test script verifies the file contents.

### Step 2: Run a single trial

```bash
harbor trial start -p tasks/hello-task -a oracle --delete
```

Flags:
- `-p tasks/hello-task` -- path to the task directory
- `-a oracle` -- use the oracle agent (runs `solution/solve.sh`)
- `--delete` -- remove the Docker container after the trial

### Step 3: Inspect the results

Trial output is stored in `./trials/<trial-name>/`. Key files:
- `result.json` -- trial metadata, agent info, rewards, and timing
- `verifier/reward.txt` -- the numeric reward (0.0 to 1.0)

### Step 4: Understand the output

The `result.json` contains structured data about the trial including the task name, agent info, start/finish timestamps, and verifier rewards. A reward of 1.0 means the task was solved correctly.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-03-running-evaluations/lesson-1-single-trial
uv sync
uv run python main.py
```

## Expected Output

```text
============================================================
  Harbor Tutorial - Module 3, Lesson 1
  Running a Single Trial
============================================================

============================================================
Checking prerequisites
============================================================
[OK] Docker is running
[OK] Harbor is installed

============================================================
Step 1: Understanding the task
============================================================
Task directory: tasks/hello-task
...

============================================================
Step 3: Running a single trial with `harbor trial start`
============================================================
Command: harbor trial start -p tasks/hello-task -a oracle --delete
Running trial...
...
Trial completed!
...

============================================================
Step 4: Inspecting the trial results
============================================================
--- result.json (key fields) ---
  trial_name:  hello-task__<id>__oracle
  task_name:   tutorial/hello-task
  rewards:     [1.0]
  exception:   None (success)

--- verifier/reward.txt ---
  Reward: 1.0
  The oracle agent solved the task perfectly!
```

## Key Takeaways

- `harbor trial start` runs one agent attempt at one task
- The oracle agent validates that your task's solution and tests work correctly
- Results are stored in `./trials/<trial-name>/` with `result.json` and verifier output
- Use `harbor trial start` for quick testing; use `harbor run` for systematic evaluations
- A reward of 1.0 means the task was solved; 0.0 means it was not

## Next Steps

Proceed to [Job Configuration with job.yaml](../lesson-2-job-config/) to learn how to run multi-trial evaluations with a configuration file.
