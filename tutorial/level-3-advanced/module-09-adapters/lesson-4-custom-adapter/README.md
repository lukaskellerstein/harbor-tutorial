# Building a Custom Adapter

**Duration:** 45 minutes

## Overview

This lesson teaches you how to build a custom adapter that converts your own benchmark data into Harbor task directories. You will create a simplified adapter that reads coding challenges from a CSV file and generates complete Harbor tasks with instruction files, Dockerfiles, test scripts, and reference solutions. While this adapter does not use the full Harbor adapter framework, it demonstrates the core conversion logic that every adapter implements.

## Prerequisites

- Completed Lesson 1: What Are Adapters?
- Completed Lesson 2: Running SWE-Bench
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running (for optional task execution)

## Concepts

### The Adapter's Job

An adapter has one job: transform benchmark data from its native format into Harbor's standard task directory structure. This means generating five files per task:

1. **instruction.md** — Natural language description of what the agent must do
2. **task.toml** — Configuration: name, metadata, timeouts, difficulty
3. **Dockerfile** — Container environment with dependencies and input files
4. **test.sh** — Verification script that writes a reward (0-1) to `/logs/verifier/reward.txt`
5. **solve.sh** — Reference solution for the oracle agent

### Scaffolding with `harbor adapter init`

Harbor provides an interactive wizard (`harbor adapter init`) that generates the boilerplate for a new adapter. It creates the standard directory structure, metadata file, and entry points. After scaffolding, you fill in the conversion logic.

### Validation with `harbor adapter review`

Before publishing, validate your adapter with `harbor adapter review`. This checks that all required files exist, configurations are valid, test scripts are executable, and Docker images build correctly.

### Our Approach

In this lesson, we build the conversion logic from scratch using a simple CSV format. This shows the fundamental pattern without the overhead of the full adapter framework. The concepts transfer directly to production adapters.

## Step-by-Step

### Step 1: Understand Adapter Scaffolding

Learn about `harbor adapter init` and the standard adapter directory structure it generates.

### Step 2: Examine the Source Data

Our CSV file contains three coding challenges with columns: id, instruction, expected_output, difficulty. Each row becomes one Harbor task.

### Step 3: Run the Adapter

The adapter reads the CSV, and for each challenge generates a complete task directory under `generated-tasks/`.

### Step 4: Inspect Generated Tasks

Examine the generated files for the first task to verify the adapter produced valid Harbor task directories.

### Step 5: Run with Oracle (Optional)

If Harbor and Docker are available, run the oracle agent against the first generated task to verify it works end-to-end.

### Step 6: Learn About Validation

Understand how to validate adapters with `harbor adapter review` and what to include for production-quality adapters.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-09-adapters/lesson-4-custom-adapter
uv sync
uv run python main.py
```

To run the generated tasks manually:

```bash
# Run a single task with oracle
harbor run -p generated-tasks/fizzbuzz -a oracle

# Run all generated tasks
harbor run -p generated-tasks -a oracle
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Level 3, Module 9          #
#          Lesson 3: Building a Custom Adapter          #
########################################################

============================================================
Step 1: Scaffolding a New Adapter
============================================================

Harbor provides an interactive wizard to scaffold adapters:

  $ harbor adapter init
  ...

============================================================
Step 2: The Source Data (challenges.csv)
============================================================

File: challenges.csv

  Columns: id, instruction, expected_output, difficulty

  Challenge 1: fizzbuzz (difficulty: easy)
    Instruction: Write a Python script called solution.py that prints numbers...
    Expected:    output contains 'FizzBuzz'

  Challenge 2: word-count (difficulty: medium)
    ...

  Challenge 3: csv-parser (difficulty: hard)
    ...

============================================================
Step 3: Running the Adapter
============================================================

Source:  challenges.csv
Output:  generated-tasks/

Converting challenges to Harbor tasks...

  Generated: fizzbuzz/
  Generated: word-count/
  Generated: csv-parser/

Total tasks generated: 3

============================================================
Step 4: Inspecting Generated Tasks
============================================================

Task: fizzbuzz/

  Directory structure:
  fizzbuzz/
  ├── instruction.md
  ├── task.toml
  ├── environment/
  │   └── Dockerfile
  ├── tests/
  │   └── test.sh
  └── solution/
      └── solve.sh

  --- instruction.md ---
    Write a Python script called solution.py that prints numbers...

  --- task.toml ---
    version = "1.0"
    [task]
    name = "coding-challenges/fizzbuzz"
    ...

============================================================
Step 5: Running Tasks with the Oracle Agent
============================================================

Running oracle agent on task: fizzbuzz
Command: harbor run -p generated-tasks/fizzbuzz -a oracle
...

============================================================
Summary
============================================================

Key takeaways:
  1. Adapters read benchmark data and generate Harbor tasks
  ...
```

## Key Takeaways

- An adapter converts benchmark data into Harbor's standard task directory format
- Use `harbor adapter init` to scaffold a new adapter with the interactive wizard
- The core logic: for each benchmark instance, generate instruction.md, task.toml, Dockerfile, test.sh, and solve.sh
- Always test generated tasks with the oracle agent before running real agents
- Validate with `harbor adapter review` before publishing
- Submit production adapters as pull requests to the Harbor repository

## Next Steps

You have completed Module 9: Adapters! Continue to **Module 10: Scaling & Cloud** to learn about cloud sandbox environments, parallel evaluation, and network policies.
