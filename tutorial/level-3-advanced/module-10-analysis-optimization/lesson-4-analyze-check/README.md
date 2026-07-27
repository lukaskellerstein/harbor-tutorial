# Task Quality Analysis

**Duration:** 30-40 minutes

## Overview

Harbor provides two LLM-powered tools for ensuring task quality and understanding agent behavior: `harbor check` validates that tasks are well-constructed before you run trials, and `harbor analyze` inspects agent trajectories after trials complete to detect reward hacking and specification issues. Together they close the feedback loop between authoring tasks and evaluating agents.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Docker installed and running
- Harbor installed (`uv tool install harbor`)
- API key for an LLM provider (for running check/analyze — the lesson explains the commands but only the oracle trial runs without a key)

## Concepts

### Task Quality Matters

A poorly written task produces misleading evaluation results. If the instruction is vague, tests incomplete, or the environment misconfigured, agent scores tell you more about the task than the agent. `harbor check` catches these problems early by having an LLM review your task files against a rubric.

### Rubrics

A rubric is a list of criteria that the evaluator LLM checks one by one. Each criterion has:

- **name** — identifier used as the key in results
- **description** — short summary of what is being checked
- **guidance** — detailed instructions telling the LLM how to evaluate and when to pass, fail, or mark not applicable

Harbor ships with an 11-criteria default rubric for `harbor check` (covering instruction completeness, test coverage, anti-cheating, dependency pinning, typos, and more) and a 2-criteria default rubric for `harbor analyze` (reward hacking and task specification). You can supply your own rubric with `-r rubric.toml`.

### Reward Hacking Detection

One of the most important uses of `harbor analyze` is detecting reward hacking — when an agent achieves a high reward without actually solving the task. For example, an agent might modify the test script, write directly to the reward file, or copy from the solution directory. The default analyze rubric specifically checks for these behaviors by reading the full agent trajectory.

### LLM-Powered Evaluation

Both tools work by running a Harbor trial where the "task" is to evaluate another task or trial. The evaluator agent (default: claude-code) reads the relevant files and produces structured JSON output with pass/fail/not_applicable outcomes and explanations for each criterion.

## Step-by-Step

### Step 1: Understanding harbor check

`harbor check` reads your task files (instruction.md, task.toml, tests/, solution/, Dockerfile) and has an LLM evaluate them against a rubric. The default rubric checks 11 criteria including whether all tested behavior is described in the instruction, whether tests cover all described behavior, and whether the task is resistant to cheating.

### Step 2: The quality-task

The lesson includes a sample task (`tasks/quality-task/`) that implements a simple calculator. It has a clear instruction, five tests (addition, subtraction, multiplication, division, division by zero), a working solution, and a minimal Dockerfile.

### Step 3: Custom Rubrics

The `rubric.toml` file defines a custom 5-criteria rubric focused on instruction completeness, test coverage, solution correctness, environment setup, and anti-cheating. Custom rubrics use the `[[criteria]]` TOML array format with `name`, `description`, and `guidance` fields.

### Step 4: Understanding harbor analyze

`harbor analyze` reads completed trial trajectories and evaluates agent behavior. Its default rubric checks for reward hacking (did the agent cheat?) and task specification quality (are the instructions sufficient?). Unlike `harbor check` which validates tasks before trials, `harbor analyze` validates behavior after trials.

### Step 5: Running a Trial for Analysis

The lesson runs the oracle agent against the quality-task to generate a trial with trajectory data. This trial can then be analyzed with `harbor analyze`.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-10-analysis-optimization/lesson-4-analyze-check
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  HARBOR TUTORIAL
  Level 3 | Module 10 | Lesson 4: Task Quality Analysis
============================================================

============================================================
PREREQUISITES CHECK
============================================================
[OK] Docker is running
[OK] Harbor CLI is available

============================================================
STEP 1: Understanding harbor check
============================================================

The `harbor check` command validates task quality by having an
LLM agent read your task files and evaluate each criterion in a
rubric. ...

============================================================
STEP 2: The quality-task Under Review
============================================================

  environment/
    Dockerfile
  instruction.md
  solution/
    solve.sh
  task.toml
  tests/
    test.sh

...

============================================================
STEP 6: Running a Trial for Analysis
============================================================

Running: harbor trial start -p .../quality-task -a oracle --delete --trials-dir .../trials

  Trial reward: {'reward': 1.0}

============================================================
STEP 7: Running harbor analyze
============================================================

To analyze the trial trajectory, run:

  harbor analyze .../trials \
    -m anthropic/claude-haiku-4-5-20250929

...

============================================================
RECAP
============================================================

In this lesson you learned about two LLM-powered quality tools:
  harbor check — validates task quality BEFORE running trials
  harbor analyze — inspects agent behavior AFTER trials complete
```

## Key Takeaways

- `harbor check` validates task quality before running trials by having an LLM evaluate your task files against a rubric (default: 11 criteria, model: claude-sonnet-4-6).
- `harbor analyze` inspects agent trajectories after trials complete, checking for reward hacking and task specification issues (default: 2 criteria, model: claude-haiku-4-5).
- Custom rubrics are TOML files with `[[criteria]]` arrays containing `name`, `description`, and `guidance` for each criterion.
- Each criterion produces a structured result with `outcome` (pass/fail/not_applicable) and `explanation`.
- Together, check and analyze close the feedback loop: validate tasks, run trials, detect problems, iterate.

## Next Steps

Continue to Module 11: Advanced Workflows, starting with exec pipelines for programmatic multi-phase evaluation.
