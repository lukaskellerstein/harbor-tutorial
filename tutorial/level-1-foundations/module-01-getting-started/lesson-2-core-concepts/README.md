# Core Concepts

**Duration:** 15-20 minutes

## Overview

This lesson introduces Harbor's six core building blocks: Task, Dataset, Agent, Environment, Trial, and Job. Understanding these concepts is essential before you start creating tasks and running evaluations. This is a conceptual lesson -- no Docker or evaluation runs are needed.

## Prerequisites

- Completed the [hello-harbor](../lesson-1-hello-harbor/) lesson (recommended but not required)
- No Docker or Harbor CLI needed for this lesson

## Concepts

Harbor's architecture is built on six concepts that fit together like this:

```
                    ┌──────────────────────────┐
                    │           JOB            │
                    │                          │
                    │  ┌───────┐  ┌───────┐   │
                    │  │Trial 1│  │Trial 2│   │
                    │  └───┬───┘  └───┬───┘   │
                    └──────┼──────────┼───────┘
                           │          │
                           v          v
                    Each Trial combines:
                    AGENT + TASK + ENVIRONMENT
```

### 1. Task

A Task is the fundamental unit of evaluation. It defines:
- **What** the agent should do (instruction)
- **Where** the agent works (container environment)
- **How** success is measured (test script)

Every task is a directory:

```
my-task/
├── instruction.md         # Natural language instruction
├── task.toml              # Configuration & metadata
├── environment/
│   └── Dockerfile         # Container definition
├── tests/
│   └── test.sh            # Verifier (writes reward to /logs/verifier/reward.txt)
└── solution/
    └── solve.sh           # Reference solution
```

### 2. Dataset

A Dataset is a collection of Tasks, grouped by theme or benchmark. It is simply a directory containing multiple task directories:

```
my-dataset/
├── task-001/
├── task-002/
└── task-003/
```

Run against a local dataset with `harbor run -p path/to/dataset` or a registered one with `harbor run -d org/name`.

### 3. Agent

An Agent is the program being evaluated. It reads the task instruction and attempts to complete the work inside the container. Harbor supports 37+ built-in agents:

| Category | Examples |
|----------|----------|
| Production | `claude-code`, `openhands`, `aider`, `codex`, `gemini-cli` |
| Utility | `oracle` (runs solution), `nop` (does nothing) |
| Custom | `BaseAgent` (external), `BaseInstalledAgent` (installs in container) |

### 4. Environment

An Environment is the isolated container where the agent works. It is built from the task's Dockerfile. Environment types include `docker` (local), `daytona`, `modal`, and `e2b` (cloud).

Each trial gets a fresh container -- agents cannot reuse state from previous attempts.

### 5. Trial

A Trial is a single agent attempt at a single task. It produces:
- A **reward** (0 to 1)
- An **agent trajectory** (commands and outputs)
- **config.json** and **result.json** files

### 6. Job

A Job is a collection of Trials. When you run `harbor run`, you create a job. Jobs can be configured via CLI flags or a `job.yaml` file.

## Step-by-Step

### Step 1: Read the Concept Explanations

Run the lesson script to see detailed explanations of each concept printed to the terminal:

```bash
uv run python main.py
```

### Step 2: Review the Relationship Diagram

The script includes an ASCII diagram showing how Jobs contain Trials, and how each Trial combines an Agent, Task, and Environment.

### Step 3: Explore the Hello World Task

The script inspects the task directory from the previous lesson and prints the contents of each file, explaining its purpose.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-01-getting-started/lesson-2-core-concepts
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Lesson 2                   #
#          Core Concepts                                #
########################################################

============================================================
Concept 1: TASK
============================================================
A Task is the fundamental unit of evaluation in Harbor.
...

============================================================
Concept 2: DATASET
============================================================
A Dataset is a collection of Tasks...
...

============================================================
Concept 3: AGENT
============================================================
An Agent is the program being evaluated...
...

============================================================
Concept 4: ENVIRONMENT
============================================================
An Environment is the isolated container...
...

============================================================
Concept 5: TRIAL
============================================================
A Trial is a single agent attempt at a single task...
...

============================================================
Concept 6: JOB
============================================================
A Job is a collection of trials...
...

============================================================
How Everything Fits Together
============================================================
  ┌─────────────────────────────────────────────┐
  │                    JOB                      │
  │  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
  │  │ Trial 1 │  │ Trial 2 │  │ Trial 3 │    │
  │  └────┬────┘  └────┬────┘  └────┬────┘    │
  └───────┼────────────┼────────────┼──────────┘
          v            v            v
  AGENT  +  TASK  +  ENVIRONMENT  -->  REWARD

============================================================
Summary
============================================================
Harbor's six core concepts:
  1. TASK        - What to do
  2. DATASET     - Collection of tasks
  3. AGENT       - Program that solves tasks
  4. ENVIRONMENT - Isolated container workspace
  5. TRIAL       - One agent attempt at one task
  6. JOB         - Collection of trials
```

## Key Takeaways

- Harbor has six core concepts: Task, Dataset, Agent, Environment, Trial, Job
- A Task is the fundamental unit -- it combines an instruction, a container, and a test script
- A Trial is the fundamental measurement -- one agent attempt at one task
- A Dataset groups Tasks; a Job groups Trials
- The reward (0 to 1) is written by the test script to `/logs/verifier/reward.txt`

## Next Steps

Continue to the next lesson: [Viewing Results](../lesson-3-viewing-results/) to learn how to inspect trial outcomes and use the Harbor results viewer.
