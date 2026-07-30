# Creating a Local Dataset

**Duration:** 30-40 minutes

## Overview

A dataset in Harbor is a collection of tasks organized in a single directory. In this lesson you will create a local dataset containing three tasks of varying difficulty, run the entire dataset in one command, and inspect per-task results and aggregate metrics.

## Prerequisites

- Completed Level 1 lessons (especially `task-anatomy` and `create-a-task`)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### What Is a Dataset?

A dataset is the simplest possible structure: a directory containing one or more task subdirectories. There is no special manifest file for the dataset itself. Harbor discovers tasks by scanning the directory for subdirectories that contain a `task.toml` file.

```text
my-dataset/          <-- the dataset
├── task-one/        <-- each subdirectory is a task
│   ├── task.toml
│   ├── instruction.md
│   ├── environment/Dockerfile
│   ├── tests/test.sh
│   └── solution/solve.sh
├── task-two/
│   └── ...
└── task-three/
    └── ...
```

### Local vs Registered Datasets

- **Local datasets** live on your filesystem. You point Harbor at them with `-p <path>`.
- **Registered datasets** live in the Harbor registry. You reference them with `-d "org/name"`.

This lesson focuses on local datasets. The next lesson covers registered datasets.

### Why Build Your Own Dataset?

Building a local dataset lets you:
- Test multiple related capabilities in one evaluation run
- Compare agent performance across varying difficulty levels
- Create domain-specific benchmarks for your use case
- Validate all your tasks together before publishing

## Step-by-Step

### Step 1: Understand the Dataset Structure

Our dataset contains three tasks at different difficulty levels:

| Task | Difficulty | What It Tests |
|------|-----------|---------------|
| `easy-hello` | Easy | Create a simple text file |
| `medium-reverse` | Medium | Read a file, reverse its contents, write output |
| `hard-fibonacci` | Hard | Write a Python script that generates Fibonacci numbers |

Each task follows the standard Harbor task directory structure with `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/test.sh`, and `solution/solve.sh`.

### Step 2: Examine the Tasks

Look at each task's `instruction.md` to understand what the agent must do, and each `tests/test.sh` to see how success is verified. The `solution/solve.sh` provides the reference answer that the oracle agent will run.

### Step 3: Run the Dataset

When you pass a directory to `harbor run -p`, Harbor scans it for task subdirectories and evaluates each one:

```bash
harbor run -p tasks -a oracle
```

The oracle agent runs each task's `solution/solve.sh`, and the verifier runs each task's `tests/test.sh` to produce a reward.

### Step 4: Inspect Results

Results are stored in the `jobs/` directory. Each trial has a `config.json` and `result.json` file. The lesson code parses these to show per-task rewards and aggregate metrics.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-06-datasets-benchmarks/lesson-1-local-dataset
uv sync
uv run python main.py
```

## Expected Output

```text
Step 1: Checking Prerequisites
  Docker:  [OK]
  Harbor:  [OK]

Step 2: What Is a Dataset?
  A dataset in Harbor is a directory containing task subdirectories...

Step 3: Our Dataset Structure
  tasks/
  ├── easy-hello/
  ├── medium-reverse/
  └── hard-fibonacci/

Step 4: Running the Dataset Evaluation
  Running: harbor run -p tasks -a oracle
  ... (Harbor output showing 3 trials) ...

Step 5: Inspecting Results
  Per-task results:
    harbor-tutorial/easy-hello             1.0  [PASS]
    harbor-tutorial/medium-reverse         1.0  [PASS]
    harbor-tutorial/hard-fibonacci         1.0  [PASS]

    Aggregate mean reward: 1.00
    Tasks evaluated:       3
    Tasks passed:          3
```

## Key Takeaways

- A dataset is just a directory of task subdirectories -- no special manifest needed.
- Harbor discovers tasks by scanning for `task.toml` files in subdirectories.
- Use `harbor run -p <path>` to evaluate all tasks in a local dataset.
- The oracle agent validates your dataset by running each task's reference solution.
- Results include per-task rewards and aggregate metrics for the whole dataset.

## Next Steps

Continue to `lesson-2-registered-datasets` to learn how to browse and use public benchmark datasets from the Harbor registry.
