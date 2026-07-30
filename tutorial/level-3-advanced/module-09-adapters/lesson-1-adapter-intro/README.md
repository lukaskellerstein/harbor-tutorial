# What Are Adapters?

**Duration:** 20 minutes

## Overview

Adapters are the bridge between the broader AI benchmark ecosystem and Harbor's evaluation framework. They convert external benchmarks (SWE-bench, HumanEval, GAIA, BIRD, and 80+ more) into Harbor's standard task format, allowing any agent to be evaluated against any benchmark with a single command. This lesson explains what adapters are, surveys the catalog, and walks through the conversion pipeline.

## Prerequisites

- Completed Level 1 and Level 2 of the Harbor tutorial
- Understanding of Harbor task format (Module 2: Working with Tasks)
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### Why Adapters Exist

The AI evaluation ecosystem is fragmented. Each benchmark has its own format, data source, and evaluation harness. Without adapters, every agent would need custom integration code for every benchmark — an N x M problem.

Adapters reduce this to N + M: each benchmark needs one adapter, and each agent works with Harbor's standard task format. The result is universal interoperability.

### The Adapter Pipeline

Every adapter follows the same four-stage pipeline:

1. **Fetch** — Download benchmark data from HuggingFace, GitHub, or another source
2. **Parse** — Read each benchmark instance (problem statement, tests, expected output)
3. **Convert** — Generate Harbor task files (instruction.md, task.toml, Dockerfile, test.sh, solve.sh)
4. **Output** — Write task directories to disk, ready for `harbor run`

### Adapter Directory Structure

Each adapter lives in the Harbor repository under `adapters/` and contains:

- `adapter_metadata.json` — Benchmark metadata, split sizes, parity results
- `pyproject.toml` — Python package definition
- `adapter.py` (in `src/`) — Core conversion logic
- `task-template/` — Template files that get filled in per instance
- A `.yaml` job config — Default evaluation configuration

### Using Adapters

There are two ways to use adapters:

1. **Pre-built datasets** — Many adapters have published their output as registered Harbor datasets on HuggingFace. Use `harbor dataset list` to browse, then `harbor run -d <name>`.
2. **Run the adapter yourself** — Clone the Harbor repo, install the adapter's dependencies, run the adapter to generate task directories locally.

## Step-by-Step

### Step 1: Understand the Problem Adapters Solve

The lesson begins by explaining the N x M interoperability problem and how adapters reduce it to N + M.

### Step 2: Survey the Adapter Catalog

Harbor ships with 85+ adapters covering software engineering, code generation, data/SQL, science, math, security, DevOps, and general reasoning. The lesson prints a categorized listing of major adapters.

### Step 3: Examine Adapter Structure

The lesson shows the standard directory layout of an adapter, explaining each file's role.

### Step 4: Walk Through the Pipeline

An ASCII diagram shows the four-stage pipeline (Fetch, Parse, Convert, Output) with details on what each stage produces.

### Step 5: See Usage Examples

The lesson shows CLI commands for both approaches: using pre-built registered datasets and running adapters manually.

### Step 6: List Registered Datasets

If Harbor is installed, the lesson runs `harbor dataset list` to show available pre-built datasets.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-09-adapters/lesson-1-adapter-intro
uv sync
uv run python main.py
```

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Level 3, Module 9          #
#          Lesson 1: What Are Adapters?                 #
########################################################

============================================================
What Are Adapters?
============================================================

Harbor evaluates agents by running them against tasks inside
containers. But the AI ecosystem already has dozens of popular
benchmarks — SWE-bench, HumanEval, GAIA, BIRD, and many more.

Adapters bridge this gap. An adapter takes an external
benchmark's native format and converts it into Harbor's
standard task directory structure:

  External Benchmark   -->   Adapter   -->   Harbor Tasks
  ...

============================================================
Available Adapters (85+ in Harbor)
============================================================

  Software Engineering:
    - swebench                  Real GitHub issues from popular Python repos
    ...

============================================================
Adapter Directory Structure
============================================================

  adapters/my-adapter/
  ├── adapter_metadata.json
  ...

============================================================
The Adapter Pipeline
============================================================

  ┌─────────────────────────────────────────────────────────┐
  │                  ADAPTER PIPELINE                      │
  │  1. FETCH ... 2. PARSE ... 3. CONVERT ... 4. OUTPUT   │
  └─────────────────────────────────────────────────────────┘

============================================================
Summary
============================================================

Key takeaways:
  1. Adapters convert external benchmarks into Harbor tasks
  2. Harbor ships with 85+ adapters
  ...
```

## Key Takeaways

- Adapters solve the N x M interoperability problem between benchmarks and agents
- Harbor ships with 85+ adapters covering SE, code gen, math, science, security, and more
- Every adapter follows the same structure: adapter_metadata.json, adapter.py, task-template/
- The pipeline is always: Fetch, Parse, Convert, Output
- You can use pre-built registered datasets or run adapters yourself

## Next Steps

Proceed to the next lesson: **swe-bench-adapter** — Running SWE-Bench, the most widely used software engineering benchmark.
