# Exec Pipelines -- Compile/Map/Reduce

**Duration:** 30-40 minutes

## Overview

Harbor's `harbor exec` command is an experimental feature that compiles file paths into Harbor tasks and runs an agent against each one. It automates the creation of evaluation tasks from source files, enabling you to evaluate agents on real codebases at scale without manually scaffolding a task for every file.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Harbor installed (`uv tool install harbor`)
- Docker installed and running
- Familiarity with Harbor tasks, jobs, and agents

## Concepts

### What is `harbor exec`?

Most Harbor evaluations start with hand-crafted tasks: you write an instruction, build a Dockerfile, and create test scripts. This works well for benchmarks, but what if you want to evaluate an agent across hundreds of files in a real codebase?

`harbor exec` solves this by automating the task creation pipeline. You point it at source files and give it an instruction, and it compiles each file into a separate Harbor task, runs the agent on each, and optionally aggregates the results.

### The Three-Phase Pipeline

The Executor class orchestrates three phases:

1. **Compile** (Compiler class) -- Resolves glob patterns and directory paths into concrete file lists. For each combination of instruction and environment (Cartesian product), it generates a Harbor task directory on disk with the instruction, environment, and auto-generated verifier.

2. **Map** (Job.create + job.run) -- Creates a Harbor Job from the compiled task directories and runs the specified agent on each task in parallel. This is a standard Harbor job execution.

3. **Reduce** (optional) -- Stages the artifacts from map trials into numbered directories (0001-trial-name/, 0002-...) and compiles a single reduce task. A reduce agent processes the aggregated artifacts to produce a summary.

### ExecConfig Format

The configuration uses a structured format with `map` (required) and `reduce` (optional) sections:

```yaml
schema_version: "1.0"

map:
  compile:
    instructions:
      - text: "Review this code for bugs"    # Inline instruction
      # - path: instruction.md               # Or from file
    environments:
      - paths: ["src/*.py"]                  # Glob patterns
      # - path: ./my-environment/            # Or a directory
    artifacts:
      - "result.json"                        # Expected output artifacts
  job:
    n_concurrent_trials: 4
    agents:
      - name: claude-code
        model_name: "anthropic/claude-sonnet-4-5-20250929"

reduce:                                      # Optional
  task:
    instruction:
      text: "Summarize the review findings"
    output_dir: ./reduce-output
  job:
    agents:
      - name: claude-code
```

### CLI Flags

When not using a config file, you can pass everything as flags:

| Flag | Panel | Description |
|------|-------|-------------|
| `-p/--path` | Task Compilation | Glob patterns or directories |
| `--scan/--no-scan` | Task Compilation | Recursive directory scanning |
| `-i/--instruction` | Task Compilation | Instruction text |
| `--image` | Task Compilation | Docker image for the environment |
| `-f/--artifact` | Task Compilation | Expected artifacts |
| `-a/--agent` | Map Job | Agent to use |
| `-m/--model` | Map Job | Model to use |
| `-n/--n-concurrent` | Jobs | Concurrent trial limit |
| `--ri/--reduce-instruction` | Reduce Task | Reduce phase instruction |
| `--print-config` | Config | Print resolved config and exit |

### Auto-Inference

Harbor exec can auto-infer artifacts from instruction text. If your instruction mentions file paths like `result.json` or `/app/output.csv`, those are automatically registered as artifacts without needing the `-f` flag.

## Step-by-Step

### Step 1: Examine the Exec Configuration

The lesson includes an `exec-config.yaml` that defines a map phase to review Python files for bugs. Open it and study the structure.

### Step 2: Understand the CLI Modes

Harbor exec has two modes:
- **Config mode:** `harbor exec -c exec-config.yaml`
- **Flags mode:** `harbor exec -p "src/*.py" -i "Fix bugs" -a claude-code`

The `--print-config` flag lets you see the resolved configuration without executing.

### Step 3: Walk Through the Pipeline

Run the lesson to see the three phases explained with the sample code files. The compile phase resolves glob patterns, the map phase would create one task per file, and the optional reduce phase aggregates results.

### Step 4: Explore Sample Files

The `sample-code/` directory contains three Python files with deliberate bugs. In a real exec pipeline, each would become a separate Harbor task.

### Step 5: Advanced Patterns

The lesson covers common use cases: code review at scale, API migration testing, documentation generation, and test generation.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-12-advanced-workflows/lesson-1-exec-system
uv sync
uv run python main.py
```

## Expected Output

```
============================================================
  Harbor Exec Pipelines (Compile / Map / Reduce)
============================================================

This lesson explores `harbor exec`, an experimental feature
that compiles file paths into Harbor tasks and evaluates them.

Harbor version: harbor x.y.z

============================================================
  Step 1: The Exec Configuration File
============================================================

Harbor exec uses a YAML config (ExecConfig) with two main sections:
  - map:    compile rules + job config (required)
  - reduce: aggregation task + job config (optional)
...

============================================================
  Step 5: Simulating the Compile Phase
============================================================

Input patterns: ['sample-code/*.py']
Instructions:   1 instruction(s)

Compiled 3 file(s):
  sample-code/calculator.py  (XXX bytes)
  sample-code/data_processor.py  (XXX bytes)
  sample-code/user_service.py  (XXX bytes)

Cartesian product: 3 files x 1 instruction(s) = 3 task(s)
...
```

## Key Takeaways

- `harbor exec` automates task creation from source files -- no manual scaffolding needed.
- The pipeline has three phases: Compile (paths to tasks), Map (run agent), Reduce (aggregate).
- The ExecConfig format uses a structured `map`/`reduce` layout with compile, job, and task sections.
- The Compiler produces the Cartesian product of instructions and environments.
- `harbor exec` is experimental -- the CLI flags and behavior may change.

## Next Steps

Continue to the next lesson: [Multi-Container Tasks](../lesson-2-multi-container/) to learn how to create tasks with Docker Compose environments running multiple services.
