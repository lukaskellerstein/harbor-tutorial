# Custom Installed Agent (BaseInstalledAgent)

**Duration:** 45-60 minutes

## Overview

Learn how to build an installed agent using Harbor's `BaseInstalledAgent` class. Unlike external agents that send commands into a container from the outside, installed agents install themselves _inside_ the container and run there directly. This gives them full access to the container's filesystem and tools.

## Prerequisites

- Completed Lesson 1: Custom External Agent (BaseAgent)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### BaseInstalledAgent vs BaseAgent

| Aspect | BaseAgent | BaseInstalledAgent |
|--------|-----------|-------------------|
| Where it runs | Outside the container (host) | Inside the container |
| How it executes | `environment.exec()` | `exec_as_root()` / `exec_as_agent()` |
| Setup phase | `setup()` | `install()` (called by `setup()`) |
| Best for | Simple command orchestration | Agents needing container-local tools |

### The Install/Run Lifecycle

1. **`install()`** -- Called during setup. Install system packages with `exec_as_root()` and user-level tools with `exec_as_agent()`.
2. **`run()`** -- Called to solve the task. Use `exec_as_agent()` to run commands as the default user.

### exec_as_root vs exec_as_agent

- **`exec_as_root(environment, command)`** -- Runs as root. Use for `apt-get install`, creating system directories, modifying permissions.
- **`exec_as_agent(environment, command)`** -- Runs as the default agent user. Use for everything else.

## Step-by-Step

### Step 1: Understanding the Interface

`BaseInstalledAgent` extends `BaseAgent` with:
- `install()` -- Abstract method you must implement for agent installation
- `exec_as_root()` -- Run commands as root in the container
- `exec_as_agent()` -- Run commands as the agent user
- `@with_prompt_template` -- Optional decorator for prompt template support

### Step 2: Implementing install()

The `install()` method is where you set up everything the agent needs inside the container:

```python
async def install(self, environment: BaseEnvironment) -> None:
    # System packages (need root)
    await self.exec_as_root(environment, command="apt-get update && apt-get install -y jq")
    # User-level tools
    await self.exec_as_agent(environment, command="pip install some-tool")
```

### Step 3: Implementing run()

After installation, `run()` is called to solve the task:

```python
async def run(self, instruction, environment, context):
    await self.exec_as_agent(environment, command="jq '.result' /home/user/data.json")
```

### Step 4: Creating the Task

The task provides a JSON file that the agent must parse using the tools it installed.

### Step 5: Running the Evaluation

```bash
harbor run -p tasks/parse-json -a agent:ShellScriptAgent
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-04-custom-agents/lesson-2-installed-agent
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 4, Lesson 2         #
#     Custom Installed Agent (BaseInstalledAgent)       #
########################################################

============================================================
Step 1: What is BaseInstalledAgent?
============================================================
  BaseInstalledAgent is for agents that install themselves INSIDE
  the container environment...

============================================================
Step 2: BaseAgent vs BaseInstalledAgent
============================================================
  Feature              | BaseAgent          | BaseInstalledAgent
  ...

============================================================
Step 5: Running the Evaluation
============================================================
  Running: harbor run -p tasks/parse-json -a agent:ShellScriptAgent
  ...
```

## Key Takeaways

- `BaseInstalledAgent` installs itself inside the container via `install()`
- `install()` runs before `run()` -- use it for system packages and tool setup
- `exec_as_root()` for system packages (apt-get), `exec_as_agent()` for user commands
- The base `setup()` method calls `install()` automatically
- Installed agents are ideal when the agent needs tools installed in the container

## Next Steps

Next lesson: **lesson-3-prompt-templates** -- Structure agent prompts with Jinja2 templates and SKILL.md files.
