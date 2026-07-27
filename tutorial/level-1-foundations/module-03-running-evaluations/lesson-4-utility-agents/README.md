# Oracle & Nop Agents

**Duration:** 20-25 minutes

## Overview

Learn how to use Harbor's two utility agents -- oracle and nop -- to systematically validate that your tasks work correctly before running real agent evaluations. The oracle agent proves your solution and tests are correct; the nop agent proves your tests correctly reject unsolved tasks.

## Prerequisites

- Completed Lesson 3: Built-in Agents
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### The Oracle Agent

The **oracle** agent runs the reference solution (`solution/solve.sh`) inside the task container. It answers the question: *"Do my tests pass when the correct solution is applied?"*

If the oracle gets reward 1.0, three things are confirmed:
1. Your solution script produces the correct output
2. Your test script correctly validates that output
3. Your Dockerfile builds a working environment

If the oracle gets reward less than 1.0, the problem is in your task setup, not the agent.

### The Nop Agent

The **nop** (no-operation) agent does absolutely nothing -- its `setup()` and `run()` methods are empty. It answers: *"Do my tests correctly reject when no work is done?"*

If nop gets reward 0.0, two things are confirmed:
1. Your tests detect that the task remains unsolved
2. The environment does not accidentally contain the answer

If nop gets reward greater than 0.0, your tests are too lenient or your environment leaks the solution.

### The Validation Workflow

Before evaluating real agents against your tasks:

1. Run with **nop** -- expect reward 0.0 (tests reject unsolved state)
2. Run with **oracle** -- expect reward 1.0 (solution + tests work)
3. Both pass? Your task is validated. Run real agents.

This catches common task authoring bugs: tests that always pass, solutions that do not work, broken Dockerfiles, and environments that leak answers.

## Step-by-Step

### Step 1: Understand the oracle agent

The oracle uploads `solution/solve.sh` into the container, makes it executable, and runs it. No API keys needed.

### Step 2: Understand the nop agent

The nop agent has empty `setup()` and `run()` methods. It only tests that the environment builds and that the verifier runs correctly against an untouched container.

### Step 3: Review the task

The lesson includes a FizzBuzz task in `tasks/validated-task/`. The agent must create a Python script that prints the FizzBuzz sequence for numbers 1-20.

### Step 4: Run with oracle

```bash
harbor trial start -p tasks/validated-task -a oracle --delete
```

Expected: reward 1.0 (the solution script creates a correct `fizzbuzz.py`)

### Step 5: Run with nop

```bash
harbor trial start -p tasks/validated-task -a nop --delete
```

Expected: reward 0.0 (no `fizzbuzz.py` is created, so the test fails)

### Step 6: Compare results

The lesson displays both results side by side, confirming that the task is properly validated.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-03-running-evaluations/lesson-4-utility-agents
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  Harbor Tutorial - Module 3, Lesson 4
  Oracle & Nop Agents
============================================================

============================================================
Step 4: Running with the oracle agent
============================================================
Running oracle trial...
Trial completed!
Rewards: [1.0]

============================================================
Step 5: Running with the nop agent
============================================================
Running nop trial...
Trial completed!
Rewards: [0.0]

============================================================
Step 6: Comparing results
============================================================
                          Oracle             Nop
  --------------------  ---------------  ---------------
  Agent                          oracle             nop
  Reward                            1.0             0.0
  Exception                        None            None

  VALIDATION PASSED
  - Oracle got 1.0: solution and tests are correct
  - Nop got 0.0: tests correctly reject unsolved tasks
  - This task is ready for real agent evaluation!
```

## Key Takeaways

- The oracle agent runs `solution/solve.sh` to validate that tests work with the correct solution
- The nop agent does nothing, validating that tests reject unsolved tasks
- Always run both oracle (expect 1.0) and nop (expect 0.0) before evaluating with real agents
- This validation workflow catches task authoring bugs early: leaky environments, lenient tests, broken solutions
- Neither agent requires API keys or model specification

## Next Steps

You have completed Module 3: Running Evaluations! Proceed to Module 4: Building Custom Agents to learn how to create your own Harbor agents.
