# Hello Harbor: Installation & First Run

**Duration:** 20-30 minutes

## Overview

In this lesson you will install Harbor, verify that your environment is correctly configured, and run your very first evaluation. By the end you will have seen Harbor build a container, run an agent, execute a test, and produce a reward score.

## Prerequisites

- Python 3.12+ installed
- Docker Desktop installed and running
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Concepts

### What is Harbor?

Harbor is an open-source framework for evaluating AI agents and language models. It runs agents against tasks inside Docker containers and measures how well they perform.

The evaluation loop works like this:

1. Harbor reads a **task** (an instruction, a container, and a test script)
2. It spins up a fresh Docker container as the **environment**
3. An **agent** reads the instruction and works inside the container
4. A **verifier** (test script) checks the agent's work and assigns a **reward** (0 to 1)

### Why Docker?

Every evaluation runs inside an isolated container. This ensures:
- Agents cannot access the host filesystem
- Each attempt starts from a clean state
- Results are reproducible across machines

### The Oracle Agent

For this first lesson we use the `oracle` agent. Oracle is a special utility agent that simply runs the reference solution (`solution/solve.sh`). It is useful for verifying that your task is set up correctly before testing real agents.

## Step-by-Step

### Step 1: Install Harbor

If you have not installed Harbor yet, run:

```bash
uv tool install harbor
```

Verify the installation:

```bash
harbor --version
```

### Step 2: Verify Docker

Make sure Docker Desktop is running:

```bash
docker info
```

If this prints system information, Docker is ready. If it shows an error, start Docker Desktop.

### Step 3: Understand the Task

This lesson includes a simple hello-world task in `tasks/hello-world/`:

```text
tasks/hello-world/
├── instruction.md      # "Create a file called hello.txt with 'Hello, world!'"
├── task.toml           # Configuration (name, difficulty, timeouts)
├── environment/
│   └── Dockerfile      # FROM ubuntu:24.04, WORKDIR /app
├── tests/
│   └── test.sh         # Checks /app/hello.txt exists with correct content
└── solution/
    └── solve.sh        # echo "Hello, world!" > /app/hello.txt
```

The test script (`test.sh`) checks whether the agent created the correct file and writes a reward:
- `1` to `/logs/verifier/reward.txt` if the file exists with the right content
- `0` if it does not

### Step 4: Run the Evaluation

```bash
harbor run -p tasks/hello-world -a oracle
```

Harbor will:
1. Build a Docker image from `environment/Dockerfile`
2. Start a container from that image
3. Run the oracle agent (which executes `solution/solve.sh`)
4. Run the verifier (`tests/test.sh`) to check the result
5. Report the reward

### Step 5: Run the Lesson Script

The lesson script automates all of the above and adds explanations:

```bash
cd tutorial/level-1-foundations/module-01-getting-started/lesson-1-hello-harbor
uv sync
uv run python main.py
```

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-01-getting-started/lesson-1-hello-harbor
uv sync
uv run python main.py
```

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Lesson 1                   #
#          Hello Harbor: Installation & First Run       #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Python version: 3.12.x
  [OK] Python 3.12+ detected
  [OK] Docker is installed and running
  Harbor version: harbor x.x.x
  [OK] Harbor CLI is installed

All prerequisites met! Ready to run your first evaluation.

============================================================
Step 2: Understanding the Hello World Task
============================================================
Task directory: .../tasks/hello-world

Directory structure:
  tasks/hello-world/
  ├── instruction.md      # What the agent must do
  ├── task.toml           # Task configuration
  ├── environment/
  │   └── Dockerfile      # Container the agent works in
  ├── tests/
  │   └── test.sh         # Verifier script (produces reward)
  └── solution/
      └── solve.sh        # Reference solution

Instruction (instruction.md):
  "Create a file called hello.txt with "Hello, world!" as the content."

============================================================
Step 3: Running Your First Evaluation
============================================================
Running: harbor run -p .../tasks/hello-world -a oracle
...
Evaluation completed successfully!

============================================================
Summary
============================================================
Congratulations! You just ran your first Harbor evaluation.
```

## Key Takeaways

- Harbor evaluates agents by running them against tasks in Docker containers
- A task consists of an instruction, a Dockerfile, a test script, and optionally a reference solution
- The oracle agent runs the reference solution -- useful for validating task setup
- The reward is a number from 0 (fail) to 1 (pass) written by the test script
- Docker must be running for any Harbor evaluation to work

## Next Steps

Continue to the next lesson: [Core Concepts](../lesson-2-core-concepts/) to understand the six building blocks of Harbor.
