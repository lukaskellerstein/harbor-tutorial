# Task Directory Structure

**Duration:** 15-20 minutes

## Overview

Every Harbor evaluation starts with a task. In this lesson you will learn the anatomy of a Harbor task directory -- the five files that define what an agent must do, the environment it works in, and how its work is verified. Understanding this structure is essential before you create your own tasks.

## Prerequisites

- Completed Module 1 (Getting Started)
- Harbor CLI installed (`harbor --version`)
- Docker installed and running

## Concepts

### What Is a Task?

A task is the fundamental unit of evaluation in Harbor. It packages everything needed to test an agent on a single problem:

- **What to do** -- the instruction
- **Where to do it** -- the container environment
- **How to check** -- the test script
- **What right looks like** -- the reference solution

### The Five Components

Every task directory follows the same structure:

```
task-name/
├── instruction.md         # Natural-language instruction for the agent
├── task.toml              # Configuration and metadata
├── environment/
│   └── Dockerfile         # Container definition
├── tests/
│   └── test.sh            # Verifier script (writes reward 0-1)
└── solution/
    └── solve.sh           # Reference solution (optional)
```

These five components work together in a pipeline: Harbor builds the container, gives the instruction to the agent, lets the agent work, then runs the test script to measure success.

### The Reward File

The test script is the critical piece. It must write a floating-point number between 0 and 1 to `/logs/verifier/reward.txt` inside the container. This number is the trial's reward:

- `1` = the agent fully completed the task
- `0` = the agent failed
- Values between 0 and 1 indicate partial success

## Step-by-Step

### Step 1: Examine the Directory Tree

This lesson includes an example task in `tasks/example-task/`. The task asks an agent to create a Python script that counts words in a text file.

Run the lesson to see the directory tree and verify all components are present.

### Step 2: Read Each Component

The lesson script reads and displays each file, explaining its purpose:

1. **instruction.md** -- The agent receives this text and nothing else. It must be clear and self-contained.
2. **task.toml** -- Configures the task name, timeouts, difficulty, and metadata.
3. **environment/Dockerfile** -- Defines the container. Pre-installs tools and creates input files.
4. **tests/test.sh** -- Runs after the agent finishes. Checks the output and writes a reward.
5. **solution/solve.sh** -- A known-good solution. Used by the oracle agent to validate the task.

### Step 3: Understand the Pipeline

The five components connect in this order:

```
Build Dockerfile -> Send instruction to agent -> Agent works in container
-> Upload and run test.sh -> Read reward from /logs/verifier/reward.txt
```

The solution directory is NOT used during normal evaluation. It exists only for the oracle agent and for human reference.

### Step 4: Review task.toml Fields

Key fields in `task.toml`:

| Section | Field | Purpose |
|---------|-------|---------|
| `[task]` | `name` | Unique identifier in `org/name` format |
| `[metadata]` | `difficulty` | Task difficulty (`easy`, `medium`, `hard`) |
| `[agent]` | `timeout_sec` | Maximum time the agent can work |
| `[verifier]` | `timeout_sec` | Maximum time for the test script |
| `[environment]` | `build_timeout_sec` | Maximum time to build the Docker image |

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-1-task-anatomy
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 2, Lesson 1         #
#          Task Directory Structure                     #
########################################################

============================================================
Step 1: Task Directory Structure
============================================================

A Harbor task is a directory with five components:

  example-task/
  ├── instruction.md         # What the agent must do
  ├── task.toml              # Configuration and metadata
  ├── environment/
  │   └── Dockerfile         # Container definition
  ├── tests/
  │   └── test.sh            # Verifier (writes reward 0-1)
  └── solution/
      └── solve.sh           # Reference solution (optional)

  [OK] instruction.md
  [OK] task.toml
  [OK] environment/Dockerfile
  [OK] tests/test.sh
  [OK] solution/solve.sh

  All five components are present.

============================================================
Step 2: Examining Each Component
============================================================
  ...
  (contents of each file displayed with explanation)
  ...

============================================================
Step 3: How the Components Connect
============================================================
  1. BUILD      environment/Dockerfile
  2. INSTRUCT   instruction.md
  3. SOLVE      (agent works inside the container)
  4. VERIFY     tests/test.sh
  5. REWARD     /logs/verifier/reward.txt

============================================================
Summary
============================================================
A Harbor task directory has five components:
  instruction.md, task.toml, environment/, tests/, solution/
```

## Key Takeaways

- A Harbor task is a directory with five components: instruction, configuration, environment, tests, and solution
- The instruction is the ONLY information the agent receives
- The test script must write a reward (0-1) to `/logs/verifier/reward.txt`
- `task.toml` controls timeouts, metadata, and the task name
- The solution is optional but recommended for validating tasks with the oracle agent

## Next Steps

Continue to the next lesson: [Scaffolding a Task](../lesson-2-create-a-task/) to build your own task from scratch.
