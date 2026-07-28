# Judging the Process, Not Just the Output

**Duration:** 45-55 minutes

## Overview

Every grading technique so far looked at what the agent left behind. None of them can tell "wrote a script that sorts" from "read eight numbers and typed them out in order" — both leave an identical `sorted.txt`. This lesson grades the *process* using the agent's trajectory, then turns around and asks an uncomfortable question: the agent and the verifier share a filesystem, so what stops the agent from just writing the reward itself?

## Prerequisites

- Completed [Custom Criteria & Multi-Dimensional Rewards](../lesson-5-custom-criteria/)
- Docker installed and running
- **LiteLLM gateway running** — `cd infra && docker compose up -d litellm`

## Concepts

### The trajectory is evidence

Harbor agents write an ATIF trajectory to `/logs/agent/trajectory.json`:

```json
{"schema_version": "ATIF-v1.7",
 "agent": {"name": "claude-code", "model_name": "claude-sonnet-4-5-20250929"},
 "steps": [{"step_id": 2, "source": "agent",
            "tool_calls": [{"function_name": "Write", "arguments": {...}}]}]}
```

Three built-in criteria read it:

| Criterion | Returns |
|-----------|---------|
| `trajectory_tool_used(tool, min_count=1)` | bool — agent called this tool |
| `trajectory_tool_not_used(tool)` | bool — agent avoided it |
| `trajectory_turn_count(max_turns)` | **float** — `1.0` at or under `max_turns`, decaying linearly to `0.0` at `2 * max_turns` |

### The path gotcha

All three default to `path="/logs/trajectory.json"`. **Harbor writes `/logs/agent/trajectory.json`** — the agent's log directory, not the root of `/logs`. The default is wrong for every Harbor task.

Worse, it fails *silently*. `load_trajectory()` returns `None` for a missing file and the criterion scores `0` with no error attached. A whole process dimension reading zero looks like a badly behaved agent, not a typo.

```python
TRAJECTORY = "/logs/agent/trajectory.json"

rk.trajectory_tool_used("Write", path=TRAJECTORY, weight=2.0)
rk.trajectory_turn_count(6, path=TRAJECTORY)
```

Always pass `path=` explicitly.

### Trajectory-aware judges — and their constraint

A rubric can hand the trajectory to the judge:

```toml
atif-trajectory = "/logs/agent/trajectory.json"
```

Note the **hyphen** — the TOML key is `atif-trajectory`, mapping to the `atif_trajectory` field. An underscore is silently ignored and the judge simply never sees it. Supplying it switches RewardKit's system prompt from `prompts/llm.md` to `prompts/llm_trajectory.md`, telling the judge it is grading reasoning and tool calls as well as the workspace.

> **This does not work through a gateway alias.** To budget how much trajectory fits in context, RewardKit calls `litellm.get_model_info(judge.model)` (`rewardkit/judges.py`), which looks the model up in litellm's built-in price/context map. A gateway alias is not in that map, and the whole dimension dies:
>
> ```
> Exception: This model isn't mapped yet. model=openai/gemma-large,
> custom_llm_provider=openai.
> ```
>
> Trajectory-aware *judging* therefore needs a judge model litellm recognizes by name — judge that dimension directly against a provider (`anthropic/claude-...`, `openai/gpt-4o`) rather than through the gateway. Do **not** name a gateway alias after a model it is not; that trades a broken thing for a lie. The programmatic `trajectory_*` criteria are unaffected and work fine through the gateway.
>
> `atif-trajectory` is therefore commented out in this lesson's rubric, with the reasoning inline.

### Reward hacking

By default the verifier runs **inside the agent's own container** — on the filesystem the agent just had write access to, including `/logs/verifier`. Nothing clears that directory first.

Combine that with Lesson 1's precedence rule and you have an exploit:

- the verifier writes its verdict to `reward.txt`
- Harbor reads `reward.json` **first**, falling back to `reward.txt`
- so a `reward.json` planted by the agent **outranks the verifier's own answer**

The entire attack:

```bash
mkdir -p /logs/verifier
echo '{"reward": 1.0}' > /logs/verifier/reward.json
```

The verifier still runs, still checks the real work, still prints `this trial FAILED` — and is silently overruled.

### Three defenses

**1. Clear the reward directory before writing to it.** One line, works in every environment mode:

```bash
mkdir -p /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/reward.txt
```

Anything already in `/logs/verifier` is untrusted input. Delete it and the verifier's verdict is the only verdict, whichever format it uses.

**2. Give the verifier its own container.**

```toml
[verifier]
environment_mode = "separate"

[verifier.environment]
docker_image = "python:3.13-slim"
network_mode = "public"       # judges need to reach their API
```

In separate mode Harbor calls `empty_dirs([verifier_dir])` before verifying (`src/harbor/trial/trial.py`), so planted reward files are wiped whether or not your `test.sh` remembers to. The verifier also runs on a filesystem the agent never touched, so it cannot be sabotaged through installed packages or shadowed binaries either.

The cost is real: the verifier no longer shares the agent's workspace, so you must declare `artifacts` for whatever it needs to see. That is a design change — which is why defense 1 is worth doing even when you also do this.

**3. Go looking for it after the fact.** `harbor analyze` ships a `reward_hacking` rubric criterion whose guidance explicitly hunts for agents writing to `/logs/verifier/reward.txt` or `reward.json`:

```bash
harbor analyze jobs/<job-dir> --failing
```

Covered in Module 11, Lesson 4.

## Step-by-Step

### Step 1: The trajectory is evidence
### Step 2: Grading the process (`tasks/trajectory-graded/`)

Three dimensions over one trial: `outcome/` (workspace), `process/` (trajectory criteria), `approach/` (judge).

> This task runs with `oracle`, which produces no trajectory — it only executes `solve.sh`. So `solve.sh` stages a **recorded** ATIF file at `/logs/agent/trajectory.json`, keeping the lesson free to run. Re-run with `-a claude-code` and the trajectory is genuinely the agent's own.

### Step 3: The attack (`tasks/reward-hacking/`)
### Step 4: The fix (`tasks/reward-hardened/`)

Byte-for-byte the same cheating `solve.sh`, the same honest test, one extra line.

## Running the Lesson

```bash
cd infra && docker compose up -d litellm      # if not already running
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-6-trajectory-judging
uv sync
uv run python main.py
```

## Expected Output

```
    ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
    ┃ Trials ┃ Exceptions ┃ Approach ┃ Outcome ┃ Process ┃ Reward ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
    │      1 │          0 │    0.958 │   1.000 │   1.000 │  0.986 │
    └────────┴────────────┴──────────┴─────────┴─────────┴────────┘

  Per criterion, grouped by dimension:

    approach  (llm)  ->  0.96
      reads_the_input                                   1.00  x3
      uses_real_sorting                                 1.00  x2
      robustness                                        0.75  x1

    outcome  (programmatic)  ->  1.00
      file_exists:sort_numbers.py                       1.00  x1
      file_matches:sorted.txt                           1.00  x1

    process  (programmatic)  ->  1.00
      trajectory_tool_used:Write                        1.00  x2
      trajectory_tool_used:Bash                         1.00  x2
      trajectory_tool_used:Read                         1.00  x1
      trajectory_turn_count:6                           1.00  x1

...

  Reward Harbor recorded: {'reward': 1.0}

  1.00. The agent did no work at all.
  The verifier's own stdout says the trial failed -- and was
  overruled by a file the agent wrote.

...

  reward-hacking  -> 1.00
  reward-hardened -> 0.00

  Same agent, same cheat, same test. One line of the verifier.
```

## Try It Yourself

Break the process dimension the way everyone breaks it once — delete `path=TRAJECTORY` from one criterion in `tasks/trajectory-graded/tests/process/how.py` and re-run. That criterion drops to `0.00` with **no error message**, because the default path does not exist. That silence is the entire reason to pass `path=` explicitly.

## Key Takeaways

- The trajectory distinguishes solving the task from producing the answer; the workspace cannot
- `trajectory_tool_used` / `_not_used` / `_turn_count` read ATIF, and `_turn_count` gives partial credit for brevity
- **Always pass `path="/logs/agent/trajectory.json"`** — the default is wrong for Harbor and fails silently
- `atif-trajectory` (hyphen!) gives a judge the agent's reasoning, but needs a judge model litellm maps — not a gateway alias
- In the default mode the agent can write `/logs/verifier/reward.json`, which outranks the verifier's own `reward.txt`
- `rm -f` the reward files at the top of `test.sh` — one line, every mode
- `environment_mode = "separate"` makes that structural, at the cost of declaring `artifacts`
- `harbor analyze --failing` hunts for reward hacking after the fact

## Next Steps

You have finished **Module 8: Grading & Rewards**. Continue to Module 9 — Adapters, to convert external benchmarks like SWE-Bench into Harbor task format. Every adapter ships a verifier, and you now know how to read one.
