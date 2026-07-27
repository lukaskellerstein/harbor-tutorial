# Custom External Agent (BaseAgent)

**Duration:** 30-45 minutes

## Overview

Learn how to build a custom external agent using Harbor's `BaseAgent` class. External agents run outside the container and send commands into the environment via `environment.exec()`. This is the simplest and most common way to create custom agents in Harbor.

## Prerequisites

- Completed Level 1 (Foundations)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### The Two Agent Types

Harbor supports two kinds of custom agents:

1. **External Agent (`BaseAgent`)** -- runs on the host machine, sends commands into the container via `environment.exec()`. This is what we build in this lesson.
2. **Installed Agent (`BaseInstalledAgent`)** -- installs itself inside the container, runs from within. Covered in the next lesson.

### BaseAgent Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│     Host Machine    │         │   Docker Container   │
│                     │  exec() │                      │
│   ┌─────────────┐   │ ──────> │   ┌──────────────┐   │
│   │  Your Agent │   │         │   │  Task Env    │   │
│   │  (BaseAgent)│   │ <────── │   │  (Dockerfile)│   │
│   └─────────────┘   │  result │   └──────────────┘   │
└─────────────────────┘         └──────────────────────┘
```

Your agent process never enters the container. Instead, it sends shell commands via `environment.exec()` and receives results back as `ExecResult` objects.

### The Agent Lifecycle

1. **`__init__()`** -- Harbor instantiates the agent with logging, model info, etc.
2. **`setup(environment)`** -- Called once before the task. Use this to install tools or prepare the environment.
3. **`run(instruction, environment, context)`** -- Execute the task. Read the instruction, send commands, populate the context with results.

### ExecResult

Every call to `environment.exec()` returns an `ExecResult` with three fields:

- `stdout: str | None` -- standard output from the command
- `stderr: str | None` -- standard error from the command
- `return_code: int` -- exit code (0 = success)

## Step-by-Step

### Step 1: Understand the BaseAgent Interface

Every external agent must implement four methods:

```python
from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

class MyAgent(BaseAgent):
    @staticmethod
    def name() -> str:
        return "my-agent"        # Unique identifier

    def version(self) -> str | None:
        return "0.1.0"           # Agent version

    async def setup(self, environment: BaseEnvironment) -> None:
        pass                     # Prepare the environment

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        # Execute the task here
        result = await environment.exec(command="echo 'hello'")
```

### Step 2: Implement the GrepAgent

Our `GrepAgent` is intentionally simple. It:

1. Explores the container filesystem with `find`
2. Creates the requested file with `echo ... > file`
3. Verifies the file was created with `cat`
4. Records metadata in `context.metadata`

See `agent.py` for the full implementation.

### Step 3: Create a Task

The task tells the agent what to do and how to verify success:

- `instruction.md` -- "Create a file at /home/user/output.txt containing 'Hello from Harbor'"
- `task.toml` -- configuration (timeouts, metadata)
- `environment/Dockerfile` -- a minimal Python 3.12 container with a `user` account
- `tests/test.sh` -- checks that `/home/user/output.txt` contains the expected text and writes a reward (0 or 1) to `/logs/verifier/reward.txt`
- `solution/solve.sh` -- reference solution for validation

### Step 4: Run the Evaluation

Harbor loads our agent class and runs it against the task:

```bash
harbor run -p tasks/write-file -a agent:GrepAgent
```

The `-a agent:GrepAgent` flag tells Harbor to import the `GrepAgent` class from `agent.py` (the module named `agent`).

### Step 5: Inspect the Results

After the evaluation, check the `jobs/` directory for results, or run:

```bash
harbor view jobs
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-04-custom-agents/lesson-1-external-agent
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 4, Lesson 1         #
#     Custom External Agent (BaseAgent)                 #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Docker: [OK]
  Harbor: [OK]

All prerequisites met!

============================================================
Step 2: Understanding BaseAgent
============================================================

Harbor has two types of custom agents:
  1. External Agent (BaseAgent)
     - Runs OUTSIDE the container, on the host machine
     ...

============================================================
Step 5: Running the Evaluation
============================================================

Command: harbor run -p tasks/write-file -a agent:GrepAgent
...
Evaluation completed successfully!

============================================================
Summary
============================================================

Key takeaways:
  - BaseAgent runs OUTSIDE the container, sends commands IN
  - Must implement: name(), version(), setup(), run()
  - environment.exec() returns ExecResult (stdout, stderr, return_code)
  - Run with: harbor run -p <task> -a module:ClassName
```

## Key Takeaways

- `BaseAgent` runs outside the container and sends commands in via `environment.exec()`
- You must implement four methods: `name()`, `version()`, `setup()`, `run()`
- `environment.exec()` returns an `ExecResult` with `stdout`, `stderr`, and `return_code`
- `context.metadata` lets you store arbitrary metadata about the agent execution
- Run your agent with: `harbor run -p <task-path> -a module:ClassName`

## Next Steps

Next lesson: **lesson-2-installed-agent** -- Build agents that install themselves inside the container using `BaseInstalledAgent`, `exec_as_root()`, and `exec_as_agent()`.
