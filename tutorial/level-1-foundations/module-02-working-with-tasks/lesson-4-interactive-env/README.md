# Debugging with Interactive Environments

**Duration:** 20-30 minutes

## Overview

When developing tasks or debugging agent failures, you need to see what the agent sees. Harbor's interactive environment feature lets you enter the same Docker container where agents work, explore the filesystem, run commands, and test your solution and test scripts manually. This is a hands-on lesson -- you will actually enter a container.

## Prerequisites

- Completed lesson: [Writing Test Scripts](../lesson-3-test-scripts/)
- Harbor CLI installed
- Docker installed and running

## Concepts

### Why Interactive Mode?

During task development, many things can go wrong:

- The Dockerfile might not install a required tool
- The test script might have a bug
- The solution might not work in the container environment
- Network access might be blocked or unavailable

Interactive mode lets you enter the container and investigate directly, rather than guessing from error messages.

### The start-env Command

```bash
harbor task start-env -p <task-dir> -e docker -i
```

This command:
1. Builds the Docker image from the task's Dockerfile
2. Starts a container
3. Copies `solution/` to `/solution` and `tests/` to `/tests` inside the container
4. Opens an interactive bash shell

When you exit the shell, Harbor automatically deletes the container.

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p, --path` | Path to the task directory (required) |
| `-e, --env` | Environment type (default: `docker`) |
| `-i, --interactive` | Start an interactive shell (default) |
| `--non-interactive` | Start the container without entering it |
| `-a, --all` | Include solution and tests (default: true) |
| `--agent` | Optionally install an agent into the environment |
| `-m, --model` | Model name for the agent |

## Step-by-Step

### Step 1: Understand the Task

This lesson includes a task in `tasks/debug-task/` that asks the agent to create a Python script that makes an HTTP request. The environment includes extra debugging tools (curl, vim, git, procps, net-tools).

### Step 2: Run the Lesson Script

The lesson script explains interactive mode and validates the task with the oracle agent:

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-4-interactive-env
uv sync
uv run python main.py
```

### Step 3: Enter the Container (Hands-On)

In a separate terminal, enter the container interactively:

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-4-interactive-env
harbor task start-env -p tasks/debug-task -e docker -i
```

Your prompt will change to something like `root@abc123:/app#`, indicating you are inside the container.

### Step 4: Explore Inside the Container

Try these commands inside the container:

```bash
# Check the working directory
pwd
ls -la

# Verify tools are installed
python --version
which curl
pip list | grep requests

# Read the solution
cat /solution/solve.sh

# Run the solution manually
bash /solution/solve.sh
cat /app/fetch_status.py

# Test the solution
python /app/fetch_status.py

# Run the test script
mkdir -p /logs/verifier
bash /tests/test.sh
cat /logs/verifier/reward.txt

# Check network connectivity
curl -I http://example.com

# Exit the container
exit
```

### Step 5: Debug a Real Problem

When an evaluation fails, use this workflow:

1. **Enter** the container with `harbor task start-env -i`
2. **Explore** the filesystem and installed tools
3. **Solve** by running the solution manually
4. **Test** by running the test script and checking the reward
5. **Fix** any issues you find, update your task files
6. **Validate** with `harbor run -p <task> -a oracle`

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-4-interactive-env
uv sync
uv run python main.py
```

Then, in a separate terminal:

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-4-interactive-env
harbor task start-env -p tasks/debug-task -e docker -i
```

## Expected Output

From `main.py`:

```text
########################################################
#          HARBOR TUTORIAL - Module 2, Lesson 4         #
#          Debugging with Interactive Environments      #
########################################################

============================================================
Step 1: What Is Interactive Mode?
============================================================
  harbor task start-env -p <task-dir> -e docker -i

============================================================
Step 2: Our Debug Task Environment
============================================================
  ... (Dockerfile contents shown) ...
  Installed tools: curl, vim, git, procps, net-tools, requests

============================================================
Step 3: Enter the Container Interactively
============================================================
  cd .../lesson-4-interactive-env
  harbor task start-env -p tasks/debug-task -e docker -i

============================================================
Step 4: Useful Debugging Commands
============================================================
  ls -la /app/
  python --version
  bash /solution/solve.sh
  bash /tests/test.sh
  cat /logs/verifier/reward.txt

============================================================
Step 5: Non-Interactive Inspection
============================================================
  Running: harbor run -p tasks/debug-task -a oracle
  ...
  Task validated successfully.

============================================================
Step 6: The Debugging Workflow
============================================================
  1. ENTER   -> 2. EXPLORE -> 3. SOLVE ->
  4. TEST    -> 5. FIX     -> 6. VALIDATE

============================================================
Summary
============================================================
  Key command: harbor task start-env -p <task-dir> -e docker -i
  This completes Module 2: Working with Tasks.
```

From the interactive session:

```text
root@abc123:/app# ls
root@abc123:/app# bash /solution/solve.sh
fetch_status solution created.
root@abc123:/app# python fetch_status.py
200
root@abc123:/app# bash /tests/test.sh
Script output: 200
response.html size: 1256 bytes
PASS: Script ran and saved response
root@abc123:/app# cat /logs/verifier/reward.txt
1
root@abc123:/app# exit
```

## Key Takeaways

- `harbor task start-env -p <task> -e docker -i` enters the same container agents use
- Inside the container, you have access to `/solution` and `/tests` for debugging
- The container is automatically cleaned up when you exit
- The debugging workflow: Enter, Explore, Solve, Test, Fix, Validate
- Interactive mode is essential for task development -- never develop tasks blind

## Next Steps

This completes Module 2: Working with Tasks. Continue to Module 3: [Running Evaluations](../../module-03-running-evaluations/lesson-1-single-trial/) to learn how to run single trials and configure evaluation jobs.
