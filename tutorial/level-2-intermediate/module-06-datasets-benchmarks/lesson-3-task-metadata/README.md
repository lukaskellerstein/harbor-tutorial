# Task Configuration Deep Dive

**Duration:** 35-45 minutes

## Overview

The `task.toml` file is the configuration heart of every Harbor task. This lesson walks through every section and field, explains what each one does, and runs a richly configured task to demonstrate how configuration affects evaluation behavior.

## Prerequisites

- Completed `lesson-1-local-dataset` and `lesson-2-registered-datasets` lessons
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running

## Concepts

### task.toml at a Glance

Every task directory must contain a `task.toml` file. It controls:

- **Identity** -- task name, description, authors (the `[task]` section)
- **Metadata** -- difficulty, category, tags, custom fields (the `[metadata]` section)
- **Agent behavior** -- timeout, user, network access (the `[agent]` section)
- **Verification** -- how tests run, timeout, environment mode (the `[verifier]` section)
- **Container setup** -- resources, image, env vars, network (the `[environment]` section)
- **Multi-step flows** -- step definitions and reward strategy (the `[[steps]]` section)
- **File collection** -- artifacts to copy out after the trial (the `[[artifacts]]` section)

### Schema Version

The `schema_version` field (currently `"1.3"`) declares the format version. Harbor uses this for backward compatibility. Previously named `version`, the field was renamed to avoid confusion with dataset versioning.

## Step-by-Step

### Step 1: [task] -- Package Identity

```toml
[task]
name = "harbor-tutorial/configured-task"
description = "A richly configured task"
authors = [
    { name = "Harbor Tutorial", email = "tutorial@example.com" }
]
keywords = ["tutorial", "configuration"]
```

The `name` field uses `org/task-name` format and must be unique in the registry. If `[task]` is omitted entirely, the directory name is used as the task name.

### Step 2: [metadata] -- Free-Form Metadata

```toml
[metadata]
difficulty = "medium"
category = "programming"
tags = ["python", "file-io"]
custom_field = "any value you want"
```

The `[metadata]` section is an open dictionary -- you can add any key-value pairs. Harbor stores them but does not enforce a schema. Useful for filtering and analysis.

### Step 3: [agent] -- Agent Phase Configuration

```toml
[agent]
timeout_sec = 120.0
user = "agent"
network_mode = "public"
```

| Field | Default | Description |
|-------|---------|-------------|
| `timeout_sec` | None (no limit) | Maximum seconds for the agent to complete the task |
| `user` | Container default | Username or UID to run the agent as |
| `network_mode` | Inherited from `[environment]` | Phase-level network override: `public`, `no-network`, or `allowlist` |
| `allowed_hosts` | None | Hostnames reachable in `allowlist` mode (supports `*.example.com` wildcards) |

### Step 4: [verifier] -- Verification Configuration

```toml
[verifier]
timeout_sec = 30.0
user = "root"
environment_mode = "shared"
```

| Field | Default | Description |
|-------|---------|-------------|
| `timeout_sec` | 600.0 | Maximum seconds for the test script |
| `env` | `{}` | Environment variables for the verifier |
| `user` | Container default | Username/UID to run the verifier as |
| `environment_mode` | `"shared"` | `"shared"` runs in agent container; `"separate"` runs in its own container |

When `environment_mode = "separate"`, you can define `[verifier.environment]` with a full container specification, useful when verification needs tools the agent should not access.

### Step 5: [environment] -- Container Configuration

```toml
[environment]
build_timeout_sec = 300.0
docker_image = "python:3.12"
os = "linux"
cpus = 1
memory_mb = 512
storage_mb = 2048
gpus = 0
network_mode = "public"
workdir = "/workspace"
```

| Field | Default | Description |
|-------|---------|-------------|
| `build_timeout_sec` | 600.0 | Dockerfile build timeout |
| `docker_image` | None | Pre-built image (makes Dockerfile optional) |
| `os` | `"linux"` | Target OS (`"linux"` or `"windows"`) |
| `cpus` | None | CPU core limit |
| `memory_mb` | None | Memory limit in megabytes |
| `storage_mb` | None | Disk limit in megabytes |
| `gpus` | None | GPU count |
| `gpu_types` | None | Acceptable GPU types (e.g., `["H100", "A100"]`) |
| `network_mode` | `"public"` | Baseline network policy |
| `workdir` | None | Override container WORKDIR |

### Step 6: [environment.env] -- Environment Variables

```toml
[environment.env]
GREETING_NAME = "Harbor"
API_KEY = "${OPENAI_API_KEY}"
DB_URL = "${DB_URL:-localhost}"
```

Supports `${VAR}` template syntax to resolve values from the host at runtime. Use `${VAR:-default}` for fallback values. This is how you pass API keys into tasks without hardcoding them.

`[solution.env]` works the same way but is only used by the oracle agent.

### Step 7: [[steps]] -- Multi-Step Tasks

```toml
[[steps]]
name = "setup"
[steps.agent]
timeout_sec = 60.0

[[steps]]
name = "implement"
[steps.agent]
timeout_sec = 300.0
```

Each step has its own instruction and test script in `steps/{name}/`. The `multi_step_reward_strategy` field controls how step rewards combine: `"mean"` (default) averages them; `"final"` uses only the last step's reward.

### Step 8: [[artifacts]] -- File Collection

```toml
[[artifacts]]
source = "/workspace/output"
destination = "output"
exclude = ["*.pyc", "__pycache__"]
```

Artifacts are collected from the container after the trial and saved to the trial's `artifacts/` directory. Useful for capturing agent-produced files for post-evaluation analysis.

### Step 9: Run the Configured Task

The lesson runs a task that uses `[environment.env]` to pass a `GREETING_NAME` variable, along with custom timeouts and resource limits.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-06-datasets-benchmarks/lesson-3-task-metadata
uv sync
uv run python main.py
```

## Expected Output

```
Step 2: The task.toml File
  (displays the full task.toml contents)

Step 3: schema_version
  schema_version = "1.3"

Step 4-12: Configuration Sections
  (detailed explanation of each section)

Step 13: Running the Configured Task
  Running: harbor run -p tasks/configured-task -a oracle
  ... (Harbor output) ...
  Result: reward = 1.0 [PASS]
```

## Key Takeaways

- `task.toml` is the single configuration file for every Harbor task.
- `[task]` identifies the task with `org/name` format for the registry.
- `[metadata]` is free-form -- add any key-value pairs for filtering and analysis.
- `[agent]` and `[verifier]` control timeouts, users, and network access per phase.
- `[environment]` sets resource limits, base image, and container configuration.
- `[environment.env]` passes variables with `${VAR}` host substitution.
- `[[steps]]` enables multi-step tasks with per-step instructions and tests.
- `[[artifacts]]` collects files from the container for post-trial analysis.

## Next Steps

Continue to `lesson-4-hf-datasets` to run a dataset straight from a git repository -- including Hugging Face -- with the `--repo` flag.
