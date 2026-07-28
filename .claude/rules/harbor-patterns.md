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

## RewardKit (declarative verifiers)

Source: `packages/rewardkit/` in the Harbor repo. Published as `harbor-rewardkit`, executable is `rewardkit`.

**Invocation from `tests/test.sh` — always use the `--from` form:**
```bash
#!/bin/bash
uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
```
`uvx harbor-rewardkit@0.1` FAILS — package name and executable name differ. (The published docs
show the broken form; `skills/create-task/SKILL.md` has the correct one.)

**Tests directory layout** — each subdirectory of `/tests` becomes one named reward. A flat
layout (no subdirectories) produces a single reward named `reward`.
```
tests/
  test.sh
  criteria.py          # @criterion(shared=True) helpers, importable by subdirs
  reward.toml          # [[reward]] blocks: aggregate dimensions into extra keys
  correctness/check.py # -> reward key "correctness"
  quality/judge.toml   # -> reward key "quality"
```

**Programmatic criteria** — every built-in accepts `weight=`, `name=`, `isolated=`:
```python
import rewardkit as rk

rk.file_exists("output.txt", weight=2.0)
rk.command_succeeds("python main.py", isolated=True)
rk.json_key_equals("results.json", "most_common", "the")
```
Built-ins (23): `file_exists`, `file_not_exists`, `file_contains`, `file_contains_regex`,
`file_matches`, `files_equal`, `diff_ratio`, `command_succeeds`, `command_output_contains`,
`command_output_matches`, `command_output_matches_regex`, `json_key_equals`, `json_path_equals`,
`csv_cell_equals`, `xlsx_cell_equals`, `sqlite_query_equals`, `http_status_equals`,
`http_response_contains`, `image_similarity`, `image_size_equals`, `trajectory_tool_used`,
`trajectory_tool_not_used`, `trajectory_turn_count`.

Return types: `bool` -> 1.0/0.0; `int`/`float` used verbatim (NOT clamped); anything else raises.

**Custom criteria:**
```python
from pathlib import Path
from rewardkit import criterion

@criterion(description="output has at least {n} lines")
def has_n_lines(workspace: Path, n: int) -> bool:
    return len((workspace / "output.txt").read_text().splitlines()) >= n
```
Call through the module (`rk.has_n_lines(10)`), never directly. Use `@criterion(shared=True)` for
helpers defined in a root-level `tests/*.py` when subdirectories exist — otherwise `discover()` raises.

**Judge rubric TOML** — a `.toml` is treated as a rubric only if it has BOTH `[judge]` and `[[criterion]]`:
```toml
[judge]
judge = "openai/gemma-large"   # LiteLLM model string, or "claude-code"/"codex" for an agent judge
files = ["/app/main.py"]
mode = "batched"               # "individual" required if any criterion sets its own `files`
atif-trajectory = "/logs/agent/trajectory.json"   # note the HYPHEN in TOML

[[criterion]]
name = "edge_cases"
description = "Does the code handle empty input?"
type = "binary"                # binary | likert (+points) | numeric (+min/max)
weight = 2.0

[scoring]
aggregation = "all_pass"       # weighted_mean | all_pass | any_pass | threshold | required_pass
```

**Judge model override without editing files:** `REWARDKIT_JUDGE` / `--judge` and
`REWARDKIT_MODEL` / `--model` take precedence over the TOML.

**Outputs:** `/logs/verifier/reward.json` (scores Harbor reads) and `/logs/verifier/reward-details.json`
(per-criterion value, reasoning, errors — rendered by `harbor view jobs`).

## Key Facts

- **`reward.json` takes precedence over `reward.txt`** when both exist (`src/harbor/verifier/verifier.py`).
  The published docs claim the opposite — trust the source.
- `reward.txt` holds a single float, always keyed `"reward"`. `reward.json` holds any
  `{name: number}` map, enabling multi-dimensional rewards.
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
