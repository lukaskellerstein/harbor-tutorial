# Viewing Results: Exploring Trial Output

**Duration:** 20-30 minutes

## Overview

After running an evaluation, Harbor stores detailed results in the `jobs/` directory. This lesson teaches you how to navigate that directory, read trial configuration and outcomes, and use the Harbor results viewer for interactive exploration.

## Prerequisites

- Completed the [hello-harbor](../lesson-1-hello-harbor/) lesson
- Docker Desktop installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### Where Results Live

Every time you run `harbor run`, Harbor creates a job directory under `jobs/`. Each job contains one or more trial directories, and each trial contains everything you need to understand what happened:

```
jobs/
└── <job-name>/
    └── <trial-id>/
        ├── config.json           # What was evaluated
        │                         #   - agent name and settings
        │                         #   - task name and path
        │                         #   - environment configuration
        │
        ├── result.json           # What happened
        │                         #   - reward (0-1)
        │                         #   - status (success/error)
        │                         #   - duration
        │                         #   - any errors
        │
        ├── agent/                # Agent trajectory
        │   └── ...               #   - commands executed
        │                         #   - outputs received
        │                         #   - reasoning traces
        │
        └── verifier/
            └── reward.txt        # Raw reward value
                                  #   Written by tests/test.sh
```

### config.json

The configuration snapshot records the exact inputs for the trial:
- Which agent was used and its settings
- Which task was being evaluated
- Which environment type was used (docker, daytona, etc.)

This makes results reproducible -- you can see exactly what was run.

### result.json

The outcome file records what happened:
- **reward**: The score from 0 (fail) to 1 (pass)
- **status**: Whether the trial completed normally or errored
- **duration**: How long the trial took

### The Results Viewer

Harbor includes a web-based UI for browsing results interactively:

```bash
harbor view jobs
```

This launches a local server where you can browse jobs, compare trials, inspect trajectories, and analyze agent performance across multiple runs.

## Step-by-Step

### Step 1: Run an Evaluation

The lesson script runs the hello-world task with the oracle agent to generate fresh results:

```bash
harbor run -p tasks/hello-world -a oracle
```

### Step 2: Explore the Jobs Directory

After the evaluation completes, the script walks the `jobs/` directory tree and prints its contents, showing you exactly where each file lives.

### Step 3: Read config.json

The script reads and displays the key fields from `config.json`:
- Agent name
- Task name
- Environment type

### Step 4: Read result.json

The script reads and displays the trial outcome:
- Reward score
- Status
- Duration

### Step 5: Check reward.txt

The raw reward value written by the test script is in `verifier/reward.txt`. The script reads and interprets it:
- `1` = the agent passed
- `0` = the agent failed
- A value between 0 and 1 = partial credit

### Step 6: Try the Results Viewer

After running the lesson, try the interactive viewer yourself:

```bash
harbor view jobs
```

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-01-getting-started/lesson-3-viewing-results
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Lesson 3                   #
#          Viewing Results: Exploring Trial Output      #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Docker running: [OK]
  Harbor CLI:     [OK]

============================================================
Step 2: Running an Evaluation
============================================================
Running: harbor run -p .../tasks/hello-world -a oracle
...
Evaluation completed successfully!

============================================================
Step 3: Exploring the Jobs Directory
============================================================
Jobs directory: .../jobs

Harbor stores all evaluation results in the jobs/ directory.
...
Actual contents of your jobs/ directory:
  ├── config.json
  ├── result.json
  ├── agent/
  └── verifier/
      └── reward.txt

============================================================
Step 4: Inspecting Trial Results
============================================================
----------------------------------------
config.json — Trial Configuration
----------------------------------------
  Agent:       oracle
  Task:        tutorial/hello-world
  Environment: docker

----------------------------------------
result.json — Trial Outcome
----------------------------------------
  Reward:   1
  Status:   success
  Duration: ...s

----------------------------------------
reward.txt — The Final Score
----------------------------------------
  Reward: 1
  Interpretation: The agent PASSED (full marks)

============================================================
Step 5: The Harbor Results Viewer
============================================================
To launch the viewer, run:
  harbor view jobs

============================================================
Summary
============================================================
  1. The jobs/ directory stores all evaluation results
  2. Each trial has config.json (inputs) and result.json (outputs)
  3. reward.txt contains the score (0 = fail, 1 = pass)
  4. The agent/ subdirectory contains the agent's trajectory
  5. 'harbor view jobs' launches an interactive results viewer
```

## Key Takeaways

- Harbor stores all results in the `jobs/` directory, organized by job and trial
- `config.json` records what was evaluated (agent, task, environment)
- `result.json` records what happened (reward, status, duration)
- `reward.txt` is the raw score written by the test script
- The `agent/` directory contains the agent's execution trajectory
- `harbor view jobs` launches a web UI for interactive result exploration

## Next Steps

You have completed Module 1: Getting Started! Continue to Module 2: Working with Tasks, starting with [Task Anatomy](../../module-02-working-with-tasks/lesson-1-task-anatomy/).
