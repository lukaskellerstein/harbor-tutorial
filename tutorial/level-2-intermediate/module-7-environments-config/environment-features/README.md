# Environment Capabilities

**Duration:** 30-40 minutes

## Overview

When you build a custom Harbor agent, the `BaseEnvironment` object is your interface to the running container. This lesson explores the key methods -- `exec()`, file uploads/downloads, and path checks -- and demonstrates them through a custom `EnvironmentExplorerAgent`.

## Prerequisites

- Completed Level 1 (Modules 1-3)
- Completed Module 4, Lesson 1 (Custom External Agent)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### The BaseEnvironment API

Every custom agent's `run()` method receives a `BaseEnvironment` object. This object represents the running container and provides async methods to interact with it.

The most important methods are:

| Method | Purpose |
|--------|---------|
| `exec(command, cwd, env, timeout_sec, user)` | Run a shell command in the container |
| `upload_file(source_path, target_path)` | Copy a file from host into the container |
| `download_file(source_path, target_path)` | Copy a file from the container to host |
| `upload_dir(source_dir, target_dir)` | Copy a directory from host into the container |
| `download_dir(source_dir, target_dir)` | Copy a directory from the container to host |
| `is_file(path)` | Check if a container path is a regular file |
| `is_dir(path)` | Check if a container path is a directory |

### ExecResult

Every call to `exec()` returns an `ExecResult` with three fields:

```python
class ExecResult(BaseModel):
    stdout: str | None    # Standard output
    stderr: str | None    # Standard error
    return_code: int      # Exit code (0 = success)
```

### The exec() Method in Detail

```python
result = await environment.exec(
    command="ls -la /app",       # Shell command to run
    cwd="/app",                  # Working directory (optional)
    env={"MY_VAR": "value"},     # Environment variables (optional)
    timeout_sec=30,              # Timeout in seconds (optional)
    user="root",                 # Run as this user (optional)
)
```

## Step-by-Step

### Step 1: Understand the BaseEnvironment API

The lesson prints each method's signature and explains its purpose. All methods are async -- you must `await` them inside your agent's `run()` method.

### Step 2: Review the EnvironmentExplorerAgent

The file `agent.py` defines a custom agent that exercises every key method:

```python
class EnvironmentExplorerAgent(BaseAgent):
    async def run(self, instruction, environment, context):
        # 1. exec() - run commands
        result = await environment.exec(command="ls -la /app/data/")

        # 2. exec() with env vars
        result = await environment.exec(
            command='echo "MY_VAR=$MY_VAR"',
            env={"MY_VAR": "harbor-demo-value"},
        )

        # 3. is_file() / is_dir() - check paths
        exists = await environment.is_file("/app/data/config.json")

        # 4. upload_file() - host to container
        await environment.upload_file(tmp_path, "/app/results/uploaded.txt")

        # 5. download_file() - container to host
        await environment.download_file("/app/data/config.json", local_path)
```

### Step 3: Validate with Oracle

The lesson first runs the task with the oracle agent to confirm the task definition is correct.

### Step 4: Run with the Explorer Agent

Then it runs the same task with our custom agent to demonstrate the API in action:

```bash
harbor run -p tasks/env-explore --agent agent:EnvironmentExplorerAgent
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-7-environments-config/environment-features
uv sync
uv run python main.py
```

## Expected Output

```
Step 1: The BaseEnvironment API

  exec(command, cwd, env, timeout_sec, user) -> ExecResult
       Run a shell command inside the container.
       ...

  upload_file(source_path, target_path)
       Copy a file from the host machine into the container.

  download_file(source_path, target_path)
       Copy a file from the container to the host machine.

  is_file(path) -> bool
       Check if a path inside the container is a regular file.

  is_dir(path) -> bool
       Check if a path inside the container is a directory.

...

Step 5: Validating with Oracle Agent
  [OK] Oracle agent passed -- task is valid

Step 6: Running with EnvironmentExplorerAgent
  [OK] Explorer agent completed successfully
```

## Key Takeaways

- The `BaseEnvironment` object is your agent's interface to the container
- `exec()` is the primary tool -- it runs commands and returns stdout, stderr, and return_code
- You can pass environment variables and timeouts to `exec()`
- `upload_file()` and `download_file()` move files between host and container
- `is_file()` and `is_dir()` are quick path-existence checks
- All environment methods are async -- always use `await`

## Next Steps

Continue to [Model Selection & LiteLLM](../model-routing/) to learn how Harbor routes model requests and how to use local models with LMStudio.
