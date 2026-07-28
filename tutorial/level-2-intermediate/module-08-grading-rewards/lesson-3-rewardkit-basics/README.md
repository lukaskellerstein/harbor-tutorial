# RewardKit: Programmatic Criteria

**Duration:** 40-50 minutes

## Overview

Lesson 1's verifier was 20 lines of bash to check three strings. Lesson 2's judge was 150 lines of Python for two criteria. Both are code you now own and must debug. RewardKit — Harbor's first-party verifier package — replaces them with declarative criteria files, gives you 23 built-in checks, weights, and a per-criterion breakdown that makes a failing verifier readable at a glance.

## Prerequisites

- Completed [Rewards & the Verifier Contract](../lesson-1-reward-contract/)
- Harbor CLI installed
- Docker installed and running

## Concepts

### One line of test.sh

```bash
#!/bin/bash
uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
```

> **Mind the `--from`.** The *package* is `harbor-rewardkit`; the *executable* is `rewardkit`. `uvx harbor-rewardkit@0.1` fails, because `uvx` looks for a command named after the package. Some published docs show that broken form. The version pin keeps runs reproducible — an unpinned verifier silently changes behavior when a new RewardKit ships.

RewardKit then discovers criteria under `/tests`, runs them against the workspace (`/app` by default), and writes two files:

| File | Contents |
|------|----------|
| `/logs/verifier/reward.json` | the scores Harbor records |
| `/logs/verifier/reward-details.json` | every criterion's value, weight, and error |

### Criteria files are executed, not imported

A criteria file has no test functions. RewardKit runs it top to bottom, and each call *registers* a check:

```python
import rewardkit as rk

rk.file_exists("wordstats.py")
rk.file_contains("wordstats.py", "def word_count")
rk.command_succeeds("python wordstats.py", weight=2.0)
```

Paths are relative to the workspace, so you never write `/app/` yourself.

Because `tests/` here has no subdirectories, this is a **flat layout**: everything contributes to a single reward named `reward`. (Lesson 5 uses subdirectories to produce several named rewards.)

### Criteria run concurrently — this will bite you

RewardKit executes criteria in an `asyncio.TaskGroup`, up to `--max-concurrent-programmatic` (default 8) at a time. **Registration order is not execution order.** This is the single most common way to write a broken RewardKit verifier:

```python
rk.command_succeeds("python wordstats.py")            # creates results.json
rk.json_key_equals("results.json", "words", 19)       # RACE -- may run first
```

That reads plausibly and fails most of the time:

```
UserWarning: json_key_equals: 'results.json' not found in workspace, assigning reward 0
```

Two correct approaches:

1. **Make the artifact the agent's job.** This lesson's task instructs the agent to run the script, so `results.json` exists before verification begins. The criteria only ever *read*.
2. **Do setup and assertion in one criterion.** A custom `@criterion` function (Lesson 5) runs as a single unit, so anything it sets up is available to its own assertions.

Lowering `--max-concurrent-programmatic` to 1 is not a fix. It is a semaphore, not a sequencer.

### Weights

Every criterion takes `weight=` (default `1.0`). Weights are **relative, not percentages**:

```python
rk.file_exists("wordstats.py")                                  # weight 1.0
rk.command_succeeds("python wordstats.py", weight=2.0)
rk.json_key_equals("results.json", "words", 19, weight=3.0)
```

A script that exists and runs but computes garbage scores well below one that works, because the correctness criteria dominate.

### Return types

- `bool` → `1.0` or `0.0`
- `int` / `float` → **used verbatim, not clamped.** A criterion returning `3.7` contributes `3.7` (with a warning). `diff_ratio` and `image_similarity` are the built-ins that return fractions.
- anything else → `TypeError`

### About `isolated=True`

Every criterion accepts `isolated=True`, which runs it against an overlayfs copy of the workspace so its side effects cannot leak. It requires either the kernel `overlay` module (needs `CAP_SYS_ADMIN`) or `fuse-overlayfs` (needs `/dev/fuse`). A stock Harbor Docker container has neither, and the criterion fails with:

```
Workspace isolation requires overlayfs but neither the kernel overlay
module nor fuse-overlayfs is available, and auto-install failed.
```

Know the flag exists; reach for it only in an environment you have deliberately privileged.

## Step-by-Step

### Step 1: What RewardKit is
The invocation, the `--from` gotcha, and the two output files.

### Step 2: The built-in criteria
All 23, grouped by what they inspect — see `criteria_catalogue.py`.

| Group | Criteria |
|-------|----------|
| Files | `file_exists`, `file_not_exists`, `file_contains`, `file_contains_regex`, `file_matches`, `files_equal`, `diff_ratio` |
| Commands | `command_succeeds`, `command_output_contains`, `command_output_matches`, `command_output_matches_regex` |
| Structured data | `json_key_equals`, `json_path_equals`, `csv_cell_equals`, `xlsx_cell_equals`, `sqlite_query_equals` |
| Network | `http_status_equals`, `http_response_contains` |
| Images | `image_similarity`, `image_size_equals` |
| Trajectory | `trajectory_tool_used`, `trajectory_tool_not_used`, `trajectory_turn_count` (Lesson 6) |

### Step 3: Criteria in practice (`tasks/wordstats/`)
An agent writes a word-statistics script. Seven criteria across structure, behavior, and correctness — then the run prints `reward-details.json`, which is where a failing verifier becomes debuggable.

### Step 4: Rewriting Lesson 1's verifier (`tasks/report-rewardkit/`)
The same report task, same scale, three lines:

```python
rk.file_contains("report.md", "## Summary")
rk.file_contains("report.md", "## Findings")
rk.file_contains("report.md", "## Conclusion")
```

`file_contains` already returns `False` when the file is missing, so even the existence check the bash version needed is gone.

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-3-rewardkit-basics
uv sync
uv run python main.py
```

No API keys and no gateway needed — every criterion here is deterministic.

## Expected Output

```
============================================================
Step 3: Criteria in Practice
============================================================

  tasks/wordstats/tests/checks.py:

    # --- structure: did the agent produce the artifact we asked for? ---
    rk.file_exists("wordstats.py")
    rk.file_contains("wordstats.py", "def word_count")
    # --- behaviour: does it actually run, and announce success? ---
    rk.command_succeeds("python wordstats.py", weight=2.0)
    rk.command_output_matches("python wordstats.py", "OK")
    # --- correctness: are the numbers right? ---
    rk.json_key_equals("results.json", "words", 19, weight=3.0)
    rk.json_key_equals("results.json", "lines", 3, weight=3.0)
    rk.json_key_equals("results.json", "top_word", "the", weight=3.0)

  $ harbor run -p tasks/wordstats -a oracle -y

    ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
    ┃ Trials ┃ Exceptions ┃  Mean ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
    │      1 │          0 │ 1.000 │
    └────────┴────────────┴───────┘

  reward.json (what Harbor records):
    reward   1.00

  reward-details.json (what actually happened):

    reward "reward"  (programmatic)  ->  1.00
      criterion                                     score  weight
      -------------------------------------------- ------ -------
      file_exists:wordstats.py                       1.00     1.0
      file_contains:wordstats.py                     1.00     1.0
      command_succeeds:python wordstats.py           1.00     2.0
      command_output_matches:python wordstats.py     1.00     1.0
      json_key_equals:results.json                   1.00     3.0
      json_key_equals:results.json                   1.00     3.0
      json_key_equals:results.json                   1.00     3.0
```

Compare that table to what `reward.json` alone tells you (`1.00`). When a real agent scores `0.36`, this table says exactly which three criteria failed — and `harbor view jobs` renders the same tree under **Verifier Logs → Rewards**.

## Try It Yourself

Break the solution and watch the breakdown change:

```bash
# Edit tasks/wordstats/solution/solve.sh to write the wrong word count,
# then re-run just that task:
uv run harbor run -p tasks/wordstats -a oracle -y
```

The reward drops to `0.36` and exactly one row in the criteria table flips to `0.00` — the weighted arithmetic is visible rather than inferred.

## Key Takeaways

- `uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests` — the `--from` is mandatory, and pin the version
- Criteria files are *executed*; each `rk.<criterion>(...)` call registers a check
- **Criteria run concurrently** — never let one depend on another's side effects
- `weight=` is relative, not a percentage; use it to make correctness outrank existence
- Numeric criteria are used verbatim and are **not** clamped to 0–1
- `reward-details.json` is what turns a failing verifier from a number into a diagnosis
- `isolated=True` needs overlayfs, which a stock Docker container cannot mount

## Next Steps

Continue to [RewardKit Judge Criteria](../lesson-4-judge-criteria/), which brings Lesson 2's LLM judge into the same declarative format — as a TOML rubric with no Python at all.
