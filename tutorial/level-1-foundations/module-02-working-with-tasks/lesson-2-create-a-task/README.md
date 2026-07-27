# Scaffolding a Task

**Duration:** 25-35 minutes

## Overview

Now that you understand the anatomy of a task directory, it is time to build one from scratch. In this lesson you will create a complete "FizzBuzz" task, write all five components, and validate that everything works by running the oracle agent.

## Prerequisites

- Completed lesson: [Task Directory Structure](../lesson-1-task-anatomy/)
- Harbor CLI installed
- Docker installed and running

## Concepts

### Task Creation Workflow

Creating a Harbor task follows a consistent workflow:

1. **Write the instruction** -- Define what the agent must do, clearly and specifically
2. **Build the environment** -- Create a Dockerfile with the tools the agent needs
3. **Write the tests** -- Define how to verify the agent's work (the reward)
4. **Write the solution** -- Provide a reference implementation
5. **Validate** -- Run the oracle agent to confirm everything works

### harbor task init

Harbor provides a scaffolding command that creates the directory structure for you:

```bash
harbor task init tutorial/my-task
```

This generates all five files with sensible defaults. You then edit them to match your specific task. Useful flags include:

| Flag | Purpose |
|------|---------|
| `-p, --tasks-dir` | Output directory (default: current directory) |
| `--no-pytest` | Use a simple bash test.sh instead of a pytest template |
| `--no-solution` | Skip the solution directory |
| `--steps N` | Scaffold a multi-step task with N steps |

In this lesson we create the files programmatically so you can see exactly what goes into each one. In practice, use `harbor task init` and edit.

### Writing Good Instructions

A good instruction is:

- **Specific** -- Tell the agent exactly where to create files and what format to use
- **Self-contained** -- The agent has no context beyond this text
- **Testable** -- The expected output must be verifiable by a script

Bad: "Write a FizzBuzz program."
Good: "Create a Python script at /app/fizzbuzz.py that prints FizzBuzz for numbers 1-100. Print one value per line."

## Step-by-Step

### Step 1: Check Prerequisites

The lesson script verifies that Docker and Harbor are available before proceeding.

### Step 2: Understand harbor task init

The script explains the scaffolding command and its flags. While we create files programmatically in this lesson, you should use `harbor task init` for your own tasks.

### Step 3: Create the FizzBuzz Task

The script creates `tasks/fizzbuzz/` with all five components:

- **instruction.md** -- Asks the agent to create `/app/fizzbuzz.py` with the standard FizzBuzz rules
- **task.toml** -- Sets the task name to `tutorial/fizzbuzz`, difficulty `easy`, 120-second timeouts
- **environment/Dockerfile** -- Uses `python:3.12-slim` with `/app` as the working directory
- **tests/test.sh** -- Checks that the output has 100 lines and verifies key positions (line 3 = "Fizz", line 5 = "Buzz", line 15 = "FizzBuzz", etc.)
- **solution/solve.sh** -- Creates the correct FizzBuzz implementation

### Step 4: Validate with the Oracle Agent

The script runs:

```bash
harbor run -p tasks/fizzbuzz -a oracle
```

This tells Harbor to:
1. Build the container from the Dockerfile
2. Run the oracle agent (which executes `solution/solve.sh`)
3. Run `tests/test.sh` to verify the output
4. Report the reward (should be 1 if everything is correct)

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-2-create-a-task
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 2, Lesson 2         #
#          Scaffolding a Task                           #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Docker CLI:     [OK]
  Docker running: [OK]
  Harbor CLI:     [OK]

  All prerequisites met.

============================================================
Step 2: The harbor task init Command
============================================================
  harbor task init <org/task-name>
  ...

============================================================
Step 3: Creating the FizzBuzz Task
============================================================
  Created directory structure:
    tasks/fizzbuzz/
    [CREATED] instruction.md
    [CREATED] task.toml
    [CREATED] environment/Dockerfile
    [CREATED] tests/test.sh
    [CREATED] solution/solve.sh

  Task created successfully!

============================================================
Step 4: Validating with the Oracle Agent
============================================================
  Running: harbor run -p tasks/fizzbuzz -a oracle
  ...
  Validation PASSED! The oracle agent solved the task
  and the test script confirmed the correct output.

============================================================
Summary
============================================================
  Task creation workflow:
    1. Write a clear instruction
    2. Build an environment with the required tools
    3. Write tests that check the expected outcome
    4. Write a reference solution
    5. Validate with: harbor run -p <task> -a oracle
```

## Key Takeaways

- Use `harbor task init` to scaffold a new task with all five components
- Instructions must be specific, self-contained, and testable
- Always validate your task with the oracle agent before testing real agents
- The test script is what determines the reward -- get it right
- Keep Dockerfiles minimal: only install what the task actually needs

## Next Steps

Continue to the next lesson: [Writing Test Scripts](../lesson-3-test-scripts/) to learn different approaches to verifying agent work.
