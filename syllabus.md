# Harbor Tutorial — Syllabus

A progressive, hands-on tutorial for learning Harbor — the open-source framework for evaluating and optimizing AI agents in container environments.

---

## Level 1: Foundations

### Module 1: Getting Started

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-hello-harbor` | Installation & First Run | Install Harbor, verify Docker, run your first evaluation with a built-in dataset and agent |
| 2 | `lesson-2-core-concepts` | Core Concepts | Understand Tasks, Datasets, Agents, Environments, Trials, Jobs — the building blocks of Harbor |
| 3 | `lesson-3-viewing-results` | Exploring Results | Use `harbor view jobs` to inspect trial outcomes, rewards, and agent trajectories |

### Module 2: Working with Tasks

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-task-anatomy` | Task Directory Structure | Understand `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/`, and `solution/` |
| 2 | `lesson-2-create-a-task` | Scaffolding a Task | Use `harbor task init` to create a new task, write an instruction, build an environment, and write a test script |
| 3 | `lesson-3-test-scripts` | Writing Test Scripts | Write verifier test scripts that produce a reward (0–1) in `/logs/verifier/reward.txt` |
| 4 | `lesson-4-interactive-env` | Debugging with Interactive Environments | Use `harbor task start-env -i` to enter a task container, explore the filesystem, run commands manually |

### Module 3: Running Evaluations

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-single-trial` | Running a Single Trial | Use `harbor trial start` to run one agent attempt, inspect the result |
| 2 | `lesson-2-job-config` | Job Configuration with `job.yaml` | Configure datasets, agents, models, concurrency, and environment settings in a job file |
| 3 | `lesson-3-builtin-agents` | Built-in Agents | Survey the 37+ built-in agents (claude-code, openhands, aider, codex, etc.) and run evaluations with them |
| 4 | `lesson-4-utility-agents` | Oracle & Nop Agents | Use the `oracle` agent to validate your tasks and `nop` to test your environment setup |

---

## Level 2: Intermediate

### Module 4: Building Custom Agents

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-external-agent` | Custom External Agent (BaseAgent) | Build an agent that sends commands into the container via `environment.exec()` |
| 2 | `lesson-2-installed-agent` | Custom Installed Agent (BaseInstalledAgent) | Build an agent that installs itself inside the container with `install()`, `exec_as_root()`, `exec_as_agent()` |
| 3 | `lesson-3-prompt-templates` | Prompt Templates | Use `@with_prompt_template` and SKILL.md files to structure agent prompts |
| 4 | `lesson-4-agent-with-llm` | LLM-Powered Custom Agent | Build a custom agent that uses an LLM (via LiteLLM) to reason about and solve tasks |

### Module 5: Evaluating Real-World Agents

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-claude-code-eval` | Evaluating Claude Code | Run the built-in `claude-code` agent against custom tasks and benchmarks, analyze trajectories and performance |
| 2 | `lesson-2-langchain-agent` | Langchain Agent in Harbor | Wrap a Langchain ReAct agent as a Harbor `BaseAgent`, run it against tasks, compare results |
| 3 | `lesson-3-langgraph-agent` | Langgraph Agent in Harbor | Wrap a Langgraph stateful graph agent as a Harbor `BaseAgent`, evaluate multi-step reasoning |
| 4 | `lesson-4-deepagents-agent` | Deepagents in Harbor | Wrap a Deepagents agent as a Harbor `BaseAgent`, evaluate it alongside other agents |
| 5 | `lesson-5-claude-sdk-agent` | Claude Agent SDK in Harbor | Wrap a Claude Agent SDK agent as a Harbor `BaseAgent`, leverage tool use and agentic loops |

### Module 6: Datasets & Benchmarks

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-local-dataset` | Creating a Local Dataset | Organize multiple tasks into a dataset, run evaluations against it |
| 2 | `lesson-2-registered-datasets` | Using Registered Datasets | Browse `harbor dataset list`, run evaluations against public benchmarks |
| 3 | `lesson-3-task-metadata` | Task Configuration Deep Dive | Master `task.toml` — metadata, timeouts, difficulty levels, tags, categories |
| 4 | `lesson-4-hf-datasets` | Datasets from Hugging Face & Git | Run a dataset straight from a git repo with `--repo`, resolve refs to commit SHAs, handle the Git LFS requirement |

### Module 7: Environments & Configuration

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-docker-environments` | Docker Environments | Customize Dockerfiles, multi-stage builds, and environment configuration |
| 2 | `lesson-2-environment-features` | Environment Capabilities | Explore `exec()`, file operations, and environment lifecycle |
| 3 | `lesson-3-model-routing` | Model Selection & LiteLLM | Understand the LiteLLM model format (`anthropic/claude-sonnet-4-5-20250929`), routing, and configuration |

### Module 8: Grading & Rewards

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-reward-contract` | Rewards & the Verifier Contract | Go beyond `reward.txt` — multi-dimensional `reward.json`, precedence rules, `[verifier]` config, how named rewards feed metrics |
| 2 | `lesson-2-llm-judge` | LLM-as-a-Judge from Scratch | Write a judge script that scores open-ended output with structured JSON, routed through the LiteLLM gateway |
| 3 | `lesson-3-rewardkit-basics` | RewardKit: Programmatic Criteria | Replace hand-written bash verifiers with declarative criteria, weights, isolation, and `reward-details.json` |
| 4 | `lesson-4-judge-criteria` | RewardKit Judge Criteria | Define TOML rubrics — binary/likert/numeric criteria, aggregation modes, and swapping judge models via env |
| 5 | `lesson-5-custom-criteria` | Custom Criteria & Multi-Dimensional Rewards | Write `@criterion` functions, split `tests/` into reward dimensions, aggregate with `reward.toml`, compare verifier variants |
| 6 | `lesson-6-trajectory-judging` | Judging the Process | Score *how* the agent worked with trajectory criteria and ATIF-aware judges; defend against reward hacking with separate verifier environments |

---

## Level 3: Advanced

### Module 9: Adapters

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-adapter-intro` | What Are Adapters? | Understand how adapters convert external benchmarks into Harbor task format |
| 2 | `lesson-2-swe-bench-adapter` | Running SWE-Bench | Use the SWE-bench adapter to evaluate agents on real-world GitHub issues |
| 3 | `lesson-3-swe-bench-claude-code` | Benchmarking Claude Code on SWE-bench | End-to-end: configure, run, and analyze a SWE-bench evaluation with the built-in claude-code agent |
| 4 | `lesson-4-custom-adapter` | Building a Custom Adapter | Scaffold and implement an adapter for a new benchmark using `harbor adapter init` |

### Module 10: Scaling & Cloud

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-cloud-environments` | Cloud Sandbox Environments | Run evaluations on Daytona, Modal, E2B, and other cloud providers |
| 2 | `lesson-2-parallel-evaluation` | Parallel Evaluation | Scale to dozens or hundreds of concurrent trials with `-n` and cloud environments |
| 3 | `lesson-3-network-policies` | Network Policies | Control egress with allowlists and network policies per container |

### Module 11: Analysis & Optimization

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-metrics` | Metrics & Aggregation | Use built-in metrics (mean, max, min, sum) and write custom metric scripts |
| 2 | `lesson-2-trajectories` | Agent Trajectories | Inspect and export agent execution traces in ATIF format |
| 3 | `lesson-3-sweeps` | Configuration Sweeps | Use `harbor sweeps run` to sweep across models, agents, and hyperparameters |
| 4 | `lesson-4-analyze-check` | Task Quality Analysis | Use `harbor analyze` and `harbor check` to validate task quality with LLM-powered analysis |

### Module 12: Advanced Workflows

| # | Lesson | Topic | What You'll Learn |
|---|--------|-------|-------------------|
| 1 | `lesson-1-exec-system` | Exec Pipelines (Compile/Map/Reduce) | Build programmatic multi-phase evaluation pipelines with `harbor exec` |
| 2 | `lesson-2-multi-container` | Multi-Container Tasks | Create tasks with Docker Compose environments running multiple services |
| 3 | `lesson-3-harbor-hub` | Hub — Sharing & Leaderboards | Upload datasets and results, browse leaderboards, download community benchmarks |

---

## Appendix

### Lesson Dependencies

```text
Level 1 is sequential: M1 → M2 → M3
Level 2 modules can be taken in any order (all depend on Level 1)
  Module 5 (Real-World Agents) depends on Module 4 (Custom Agents)
  Module 8 (Grading & Rewards) is sequential and depends on M2 L3 (Test Scripts)
Level 3 modules can be taken in any order (all depend on Level 2)
  Module 11 (Analysis & Optimization) assumes Module 8 (Grading & Rewards)
```

### Time Estimates

| Level | Estimated Time |
|-------|---------------|
| Level 1: Foundations | 4–6 hours |
| Level 2: Intermediate | 11–16 hours |
| Level 3: Advanced | 8–12 hours |
| **Total** | **23–34 hours** |

### Prerequisites

- Python 3.12+
- Docker installed and running
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- API key for at least one LLM provider (Anthropic, OpenAI, etc.)
- Basic Python knowledge
- Basic command-line familiarity
