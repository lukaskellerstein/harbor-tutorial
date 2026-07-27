# Evaluating Claude Code

**Duration:** 45-60 minutes

## Overview

Claude Code is one of Harbor's built-in agents. Unlike the custom agents you built in Module 4, built-in agents require no wrapper code -- you simply reference them by name.

This lesson has two halves. First you run Claude Code with no configuration at all and analyze its results. Then you run it against a task that ships its own Claude Code setup -- skills, a subagent, an MCP server, `CLAUDE.md`, and hooks -- all defined as project-scoped files inside the task image. The second half is where the real lesson is: **evaluating an agent the way you actually configure it**, not stripped down to defaults.

## Prerequisites

- Completed Module 4 (Building Custom Agents)
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)
- Anthropic credentials in this lesson's `.env` file (see Authentication below)

## Authentication

This lesson bills your **Claude Pro/Max subscription** rather than the pay-per-token API. Generate a long-lived subscription token once:

```bash
claude setup-token   # opens a browser; prints a token valid for one year
```

Then put it in a `.env` file in this lesson directory (git-ignored):

```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

`main.py` loads this file with `python-dotenv` at startup and passes it to `harbor run`, along with `CLAUDE_FORCE_OAUTH=1` — Harbor's switch that drops any API key so the CLI bills the subscription.

Using an API key instead is still supported: put `export ANTHROPIC_API_KEY=sk-ant-...` in `.env` and omit the OAuth token.

> **Running `harbor run -c job.yaml` directly?** The `.env` file is only loaded by `main.py`. For a direct CLI run, source it into your shell first: `source .env && export CLAUDE_FORCE_OAUTH=1`. (The `export` prefixes in `.env` exist so this works.)

## Concepts

### Built-in Agents

Harbor ships with 37+ built-in agents including `claude-code`, `openhands`, `aider`, `codex`, and many more. These agents are pre-configured to work with Harbor's evaluation pipeline. You reference them by name:

```bash
harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-4-5-20250929
```

### How Claude Code Works in Harbor

When Harbor runs the `claude-code` agent:

1. **Container setup** -- Harbor builds a Docker container from the task's Dockerfile
2. **Agent installation** -- Claude Code is installed inside the container automatically
3. **Execution** -- The agent receives the instruction and uses its tools (Bash, Read, Edit, etc.) to complete the task
4. **Verification** -- Harbor runs the test script and records the reward (0-1)

### Environment Variables

Claude Code runs *inside* the container, so it needs credentials there -- but you do **not** put them in `job.yaml` or bake them into the image (that would persist the secret in the image layers).

Harbor's built-in `claude-code` agent reads `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) from the host environment and injects it into the container's environment at the moment it invokes the CLI. That is why `job.yaml` here has no `environment.env` block at all.

The credential chain is: `.env` -> `main.py` (`load_dotenv`) -> `harbor run` subprocess -> container environment.

### What Harbor Configures For You, And What It Does Not

Real Claude Code usage means skills, subagents, MCP servers, `settings.json`, hooks, and `CLAUDE.md`. Harbor covers some of that natively:

| Surface | Harbor support |
|---|---|
| **Skills** | `--skill <dir or org/repo@ref>`, `agents[].skills`, or `[environment] skills_dir` in `task.toml` |
| **MCP servers** | `--mcp-config <.mcp.json>`, `agents[].mcp_servers`, or `[[environment.mcp_servers]]` in `task.toml` |
| **Permissions / tools / prompt** | agent kwargs: `--ak permission_mode=`, `allowed_tools`, `disallowed_tools`, `append_system_prompt`, `max_turns`, `reasoning_effort`, `max_budget_usd` |
| **Auto-memory** | `--ak memory_dir=<path in container>` |
| **Subagents, `settings.json`, hooks, plugins** | **nothing** -- you ship these yourself |

So half of it is a Harbor flag, and half of it is your problem. This lesson does *all* of it the same way instead: as ordinary project-scoped files baked into the task image, which is exactly how you configure Claude Code on your own machine.

### Where the Configuration Lives: `/app`, Not `~/.claude`

Your instinct will be to `COPY` a `.claude/` directory into the container's home directory. That does not work, and the reason is worth knowing.

Harbor sets `CLAUDE_CONFIG_DIR=/logs/agent/sessions` inside the container. `/logs/agent` is a **host-mounted volume** — it is how Harbor captures session transcripts and turns them into `trajectory.json`. So anything you bake into the user-level config directory is shadowed by the mount at run time and silently disappears. (The one exception: Harbor explicitly copies `~/.claude/skills` forward for you.)

Use **project scope** instead. `/app` is the container's `WORKDIR`, and Claude Code reads project configuration from its working directory:

| File in the image | What it does |
|---|---|
| `/app/CLAUDE.md` | project memory |
| `/app/.claude/skills/<name>/SKILL.md` | a skill |
| `/app/.claude/agents/<name>.md` | a subagent |
| `/app/.claude/settings.json` | settings + hooks |
| `/app/.mcp.json` | MCP servers |

This is the same layout you already use on your own machine, it needs no Harbor flags at all, and it leaves Harbor's trajectory capture completely untouched.

### The Workspace Trust Caveat

One thing to know before you trust the above blindly. Claude Code's documentation warns that in an **untrusted** folder, `enableAllProjectMcpServers` in a project `.claude/settings.json` is ignored: the MCP server stays at "Pending approval" and never connects. Since `claude --print` can never show the workspace trust dialog, a container would seem to be permanently untrusted.

Measured against this lesson's task, that restriction does **not** apply to the running session — the documented behavior is scoped to the `claude mcp list` and `claude mcp get` subcommands. Two runs confirm it:

- `/app` as a plain directory: 5/5, `mcp__harbor-demo__get_build_code` called
- `/app` as a **git repository with `.claude/settings.json` committed** — the exact "cloned repository cannot approve its own servers" case: still 5/5, tool still called

So project-scoped `.mcp.json` plus `enableAllProjectMcpServers` is enough. If you ever *do* hit a server stuck at "Pending approval", the escape hatch is to make `/app` the configuration home:

```yaml
agents:
  - name: claude-code
    env:
      CLAUDE_CONFIG_DIR: /app/.claude   # only if you need it
```

Harbor applies `agents[].env` as a scoped overlay that outranks the agent's own environment, so this override is supported rather than a hack. It has a real cost, though: sessions then land in `/app/.claude/projects` instead of the mounted log directory, and `trajectory.json` comes back empty. You would need a `Stop` hook copying them back:

```json
"Stop": [{"hooks": [{"type": "command",
  "command": "mkdir -p /logs/agent/sessions/projects && cp -a /app/.claude/projects/. /logs/agent/sessions/projects/ 2>/dev/null || true"}]}]
```

> A symlink from `/app/.claude/projects` to the mounted directory looks like the tidier fix. It is not: `/logs/agent` only exists at run time, so the symlink dangles at build time and Harbor's own setup step then dies with `mkdir: cannot create directory '/app/.claude/projects': File exists`, taking the whole trial with it.

Since the default works, this lesson does not use any of that — but knowing the failure mode is what lets you diagnose it in ten seconds instead of an afternoon.

### Plugins and Marketplaces

There is no project-scoped equivalent of `/plugin marketplace add`. Installing a plugin requires either `claude plugin marketplace add` at run time or the `--plugin-dir` flag, and Harbor's `claude-code` agent builds its command line from a fixed list of flags that includes neither.

The closest project-scoped option is a **skills-directory plugin**: add a `.claude-plugin/plugin.json` to a folder under `.claude/skills/`, and it loads as `<name>@skills-dir` with bundled agents, hooks, and MCP servers — which is how you would ship a bundle of all five surfaces as one versioned unit.

## Step-by-Step

### Step 1: The Unconfigured Tasks

`tasks/` holds two plain tasks that measure Claude Code with default settings:

- **hello-task** -- create a file with specific content (easy)
- **sort-list** -- write and run a Python sorting script (easy-medium)

`job.yaml` runs them. This is the baseline, and it is unchanged from the simple case:

```yaml
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929
datasets:
  - path: tasks
```

### Step 2: The Configured Task

`tasks-configured/claude-setup/` ships a full Claude Code setup inside its `environment/` directory. **The Docker build context is the task's `environment/` directory**, so every file you want to `COPY` has to live inside it:

```
tasks-configured/claude-setup/environment/
├── Dockerfile
├── CLAUDE.md                            -> /app/CLAUDE.md
├── mcp.json                             -> /app/.mcp.json
├── mcp_server/harbor_demo.py            -> /app/mcp_server/  (local stdio server)
└── claude/                              -> /app/.claude/
    ├── settings.json                       hooks + enableAllProjectMcpServers
    ├── skills/harbor-report/SKILL.md       a skill
    └── agents/fact-checker.md              a subagent
```

### Step 3: Making the Configuration Provable

A configuration that silently fails to load looks exactly like one that loaded and did nothing. So the task is built so that each surface leaves evidence, and `tests/test.sh` asserts on all five independently. The reward is the fraction that passed, so a partial score tells you *which* surface broke:

| Surface | How the verifier proves it loaded |
|---|---|
| Skill | the report follows a format specified only in `SKILL.md` |
| MCP server | the report contains a build code that exists only inside the stdio server |
| `CLAUDE.md` | the report ends with the trailer line only `CLAUDE.md` requires |
| Subagent | Claude Code wrote a `subagents/*.jsonl` transcript |
| Hooks | the `PostToolUse` hook appended to `/logs/agent/hook-events.jsonl` |

The MCP build code is the sharpest of these: nothing else in the container knows the value, so the agent cannot produce it by guessing.

> There is no `solution/` directory for this task. An oracle shell script can write the report file, but it cannot cause a subagent to run or a hook to fire — two of the five assertions are about *agent behavior*, not about artifacts on disk.

### Step 4: Run Both and Compare

```bash
uv sync
uv run python main.py
```

Or run the halves separately:

```bash
source .env && export CLAUDE_FORCE_OAUTH=1
harbor run -c job.yaml               # unconfigured baseline
harbor run -c job-configured.yaml    # project-scoped setup
```

### Step 5: Confirm the Setup Actually Loaded

The first line of the agent transcript is Claude Code's `init` event, and it lists everything the session picked up:

```bash
head -1 jobs/<latest>/claude-setup__*/agent/claude-code.txt | python3 -m json.tool | head -30
```

Look for three things:

- `"mcp_servers"` contains `harbor-demo` (not `[]`)
- `"agents"` contains `fact-checker`
- `"slash_commands"` contains `harbor-report`

### Step 6: Break It on Purpose

The assertions are only worth anything if you have watched them fail. Pick one and sabotage it:

- rename `claude/agents/fact-checker.md` — the subagent assertion fails, the other four still pass
- delete the `hooks` block from `claude/settings.json` — the hook assertion fails
- point `mcp.json` at a path that does not exist — the MCP assertion fails and the agent invents nothing, because it cannot

Each time, note that Claude Code itself reports no error. The trial completes, the agent behaves plausibly, and only the verifier notices. That is the failure mode this whole lesson exists to make visible: **misconfiguration is silent, so your verifier has to be the thing that speaks up.**

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-1-claude-code-eval
uv sync
# credentials come from .env -- see Authentication above
uv run python main.py
```

## Expected Output

```
Step 1: Checking Prerequisites
  [OK] Docker is running
  [OK] Harbor CLI is installed
  [OK] CLAUDE_CODE_OAUTH_TOKEN loaded (Claude subscription auth)

Step 3: Running Claude Code With No Configuration
  Task: tutorial/hello-task
    Reward: 1.0
  Task: tutorial/sort-list
    Reward: 1.0
  Average reward: 1.00

Step 4: The Project-Scoped Claude Code Setup
  [x] claude/settings.json                  hooks + enableAllProjectMcpServers -> /app/.claude/
  [x] claude/skills/harbor-report/SKILL.md  a skill: the report format
  [x] claude/agents/fact-checker.md         a subagent, with its own context + tools
  [x] CLAUDE.md                             project memory -> /app/CLAUDE.md
  [x] mcp.json                              MCP server registration -> /app/.mcp.json
  [x] mcp_server/harbor_demo.py             the stdio MCP server itself

Step 5: Running Claude Code With Project Config
  Task: tutorial/claude-setup
    Reward: 1.0
      PASS: skill loaded (report follows the harbor-report format)
      PASS: MCP server loaded (build code came from get_build_code)
      PASS: CLAUDE.md loaded (trailer line present)
      PASS: subagent loaded (fact-checker ran in its own context)
      PASS: hooks loaded (PostToolUse hook fired on Write/Edit)
    Duration: 95.8s

  Average reward: 1.00
  Tasks passed: 1/1
```

The configured trial costs roughly $0.12 and takes about 95 seconds on a warm image.

## Key Takeaways

- Claude Code is a built-in Harbor agent -- no custom wrapping code needed
- The `claude-code` agent injects host credentials into the container itself -- no `environment.env` entry and no secret in the image
- Harbor natively configures skills, MCP servers, permissions, and memory; it has no hook at all for subagents, `settings.json`, hooks, or plugins
- Project-scoped `.claude/` files baked into the task image cover all of them at once
- Put them at **project scope** (`/app`), not in the user config directory — Harbor's host-mounted `CLAUDE_CONFIG_DIR` would shadow anything you baked in there
- Configuration that fails to load fails **silently** -- assert on it in your verifier, or you are measuring an agent you did not configure
- Use `harbor view jobs` to explore results interactively

## Next Steps

In the next lesson, you will learn how to wrap a Langchain agent as a Harbor `BaseAgent`, bridging two different agent frameworks.
