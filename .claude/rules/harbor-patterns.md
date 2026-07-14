# Harbor Patterns and APIs

These are the correct Harbor APIs, CLI commands, and file formats. Always verify against the source code before writing lesson code.

## CLI Reference

```bash
# Installation
uv tool install harbor

# Running evaluations
harbor run -d "<org/name>" -m "<model>" -a "<agent>"               # Registered dataset
harbor run -p "<path/to/dataset>" -m "<model>" -a "<agent>"        # Local dataset
harbor run -c "<path/to/job.yaml>"                                 # From config file
harbor run -d "<org/name>" -e daytona -n 32 -m "<model>" -a "<agent>"  # Cloud + parallel

# Datasets
harbor dataset list                                  # List registered datasets

# Tasks
harbor task init <task-name>                         # Scaffold new task
harbor task start-env -p <task-dir> -e docker -i     # Interactive environment

# Trials
harbor trial start -p <task-dir> -a <agent> -m <model>   # Single trial

# Results
harbor view jobs                                     # Launch results viewer

# Adapters
harbor adapter init                                  # Interactive scaffold
```

## Task Directory Format

```
task-name/
├── instruction.md         # Natural language task for the agent
├── task.toml              # Configuration and metadata
├── environment/
│   └── Dockerfile         # Container definition
├── solution/
│   └── solve.sh           # Oracle/reference solution
└── tests/
    ├── test.sh            # Must write reward (0–1) to /logs/verifier/reward.txt
    └── test_outputs.py    # Optional pytest tests
```

## task.toml Format

```toml
version = "1.0"

[task]
name = "my-benchmark/task-001"

[metadata]
author_name = "Your Name"
author_email = "your@email.com"
difficulty = "medium"
category = "programming"
tags = ["python", "debugging"]

[agent]
timeout_sec = 1800.0

[verifier]
timeout_sec = 120.0

[environment]
build_timeout_sec = 600.0
```

## job.yaml Format

```yaml
datasets:
  - path: path/to/dataset

agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929

environment:
  type: docker
  delete: true

orchestrator:
  type: local
  n_concurrent_trials: 4
```

## Custom Agent — External (BaseAgent)

```python
from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

class MyAgent(BaseAgent):
    @staticmethod
    def name() -> str:
        return "my-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        result = await environment.exec(command="echo 'solving task'")
```

Run with: `harbor run -d "<dataset>" --agent path.to.module:MyAgent`

## Custom Agent — Installed (BaseInstalledAgent)

```python
from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

class MyInstalledAgent(BaseInstalledAgent):
    async def install(self, environment: BaseEnvironment) -> None:
        await self.exec_as_root(environment, command="apt-get update && apt-get install -y curl")
        await self.exec_as_agent(environment, command="pip install my-tool")

    @with_prompt_template
    async def run(
        self, instruction: str, environment: BaseEnvironment, context: AgentContext
    ) -> None:
        await self.exec_as_agent(environment, command=f"my-tool run '{instruction}'")
```

## Key Facts

- Model format uses LiteLLM convention: `anthropic/claude-opus-4-1`, `openai/gpt-5-mini`, etc.
- Built-in agents: `claude-code`, `copilot-cli`, `openhands`, `codex`, `aider`, `gemini-cli`, `terminus-2`, `goose`, `grok-build`, and more.
- Utility agents: `oracle` (runs solution script for testing), `nop` (no-operation).
- Results stored in `jobs/` directory by default, each trial has `config.json`, `result.json`, agent trajectory, verifier output.
- Test scripts must write a numeric reward (0 to 1) to `/logs/verifier/reward.txt`.
- Cloud sandboxes (`-e daytona`, `-e modal`, etc.) make trials I/O bounded, enabling massive parallelism.
- Adapters convert external benchmarks (SWE-Bench, GAIA, etc.) into Harbor task format. Scaffold with `harbor adapter init`.

## Source Code Paths

Always read the source before using an API:
- **CLI**: `src/harbor/cli/`
- **Agents**: `src/harbor/agents/`
- **Environments**: `src/harbor/environments/`
- **Models**: `src/harbor/models/`
- **Adapters**: `adapters/`
- **Examples**: `examples/`

All paths relative to: `/Users/lkellers/Projects/github/harbor-framework/harbor`
