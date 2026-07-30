# Rewards & the Verifier Contract

**Duration:** 30-40 minutes

## Overview

Back in Module 2 you wrote `echo 1 > /logs/verifier/reward.txt` and moved on. That is the smallest possible version of Harbor's grading contract, and it throws information away: three separate checks become one number, and you can no longer tell *which* one failed. This lesson covers the full contract — `reward.json`, multi-dimensional named rewards, how those flow into job metrics, and which file wins when a verifier writes both.

## Prerequisites

- Completed [Writing Test Scripts](../../../level-1-foundations/module-02-working-with-tasks/lesson-3-test-scripts/)
- Harbor CLI installed
- Docker installed and running

## Concepts

### Two files, one contract

A verifier talks to Harbor by leaving a file behind. There are exactly two formats:

| File | Content | Becomes |
|------|---------|---------|
| `/logs/verifier/reward.txt` | one float, e.g. `0.67` | `{"reward": 0.67}` |
| `/logs/verifier/reward.json` | flat JSON object of `{name: number}` | itself |

Harbor normalizes both into a `dict[str, float]` before anything else touches them. That means **the reward is always multi-dimensional internally** — `reward.txt` is just the one-dimensional special case, and the dimension's name (`reward`) is not yours to pick.

### Why named dimensions matter

Consider a task with three requirements. With `reward.txt` you get `0.67` and know something went wrong. With `reward.json` you get:

```json
{"sections": 1.0, "title": 0, "length": 1.0}
```

Now you know the agent writes fine but ignores formatting instructions. Same amount of verifier code; strictly more signal.

This carries all the way through to job metrics. Harbor's aggregation (`src/harbor/metrics/base.py`) branches on how many distinct reward keys it sees across the job:

- **One key** → one metric, named after the *metric type*: `{"mean": 0.67}`
- **Several keys** → one metric *per key*: `{"sections": 1.0, "title": 0.0, "length": 1.0}`

A trial whose verifier crashed contributes `None`, which counts as `0` — a crash is scored as a failure, not skipped.

### The `reward` key convention

Plenty of Harbor tooling assumes a single scalar score and looks for the literal key `"reward"`:

- `min_reward` gates in multi-step tasks
- `harbor analyze --passing` / `--failing`
- `harbor check`

If your `reward.json` has only custom dimension names, those tools find nothing. **Emit a `reward` roll-up alongside your dimensions.** Costs one line; keeps the whole ecosystem working.

### Precedence: `reward.json` wins

If a verifier writes both files, Harbor reads `reward.json` and never looks at `reward.txt`:

```python
# src/harbor/verifier/verifier.py
if self.trial_paths.reward_json_path.exists():
    rewards = self._parse_reward_json()
elif self.trial_paths.reward_text_path.exists():
    rewards = self._parse_reward_text()
else:
    raise RewardFileNotFoundError(...)
```

> **Note:** The published docs page on LLM-as-a-judge states the opposite ("reward.txt first, then reward.json as a fallback"). It is wrong. The source above and Harbor's own unit test `test_verify_prefers_reward_json_over_reward_text` both put JSON first. Step 4 of this lesson demonstrates it directly rather than asking you to take anyone's word for it.

### Configuring the verifier

The `[verifier]` section of `task.toml` controls how the verifier runs:

```toml
[verifier]
timeout_sec = 120.0        # kill the verifier after this long
user = "root"              # who runs test.sh

[verifier.env]             # environment variables handed to test.sh
API_KEY = "${API_KEY}"                 # read from the host at run time
REQUIRED_WORDS = "${REQUIRED_WORDS:-50}"  # ...with a fallback
```

`${VAR}` templating keeps secrets out of the repo: the file names the variable, your shell supplies the value.

**Anything with `[verifier.env]` triggers a confirmation prompt.** Harbor stops and asks permission before reading your host environment. That prompt has no stdin when the run is driven from a script, so scripted runs need `-y`:

```bash
harbor run -p tasks/reward-json -a oracle -y
```

## Step-by-Step

### Step 1: The contract

`main.py` prints both file formats side by side before running anything.

### Step 2: One number (`tasks/reward-txt/`)

Three section checks averaged into a single float:

```bash
FOUND=0
for SECTION in "## Summary" "## Findings" "## Conclusion"; do
    if grep -qF "$SECTION" "$REPORT" 2>/dev/null; then
        FOUND=$((FOUND + 1))
    fi
done

REWARD=$(awk "BEGIN {printf \"%.2f\", $FOUND / 3}")
echo "$REWARD" > /logs/verifier/reward.txt
```

Job metrics come back as `[{'mean': 1.0}]` — one key in, one metric out.

### Step 3: Named dimensions (`tasks/reward-json/`)

The same three checks, each keeping its identity. No JSON library needed — it is a flat object, so a heredoc does the job:

```bash
cat > /logs/verifier/reward.json <<EOF
{
  "sections": $SECTIONS,
  "title": $TITLE,
  "length": $LENGTH
}
EOF
```

Job metrics come back as `[{'length': 1.0, 'sections': 1.0, 'title': 1.0}]` — per-key aggregation.

This task deliberately omits a `reward` key so you can see what the one-dimensional tooling loses.

### Step 4: Precedence (`tasks/reward-precedence/`)

This verifier writes `reward.txt` with a deliberate lie (`0.00`) alongside a truthful `reward.json`. The trial reports the JSON scores; the `0.00` is never read.

It also adds the `reward` roll-up the previous task was missing:

```bash
ROLLUP=$(awk "BEGIN {printf \"%.2f\", ($SECTIONS + $TITLE + $LENGTH) / 3}")
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-1-reward-contract
uv sync
uv run python main.py
```

All three tasks run with the `oracle` agent, which executes `solution/solve.sh` instead of calling a model — so the results are deterministic and cost nothing.

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Level 2, Module 8          #
#          Lesson 1: Rewards & the Verifier Contract    #
########################################################

============================================================
Checking Prerequisites
============================================================
  Docker CLI:     [OK]
  Docker running: [OK]
  Harbor CLI:     [OK]

...

============================================================
Step 2: One Number (reward.txt)
============================================================

  $ harbor run -p tasks/reward-txt -a oracle -y

    ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
    ┃ Trials ┃ Exceptions ┃  Mean ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
    │      1 │          0 │ 1.000 │
    └────────┴────────────┴───────┘

  Rewards recorded on the trial:
    reward   1.00

  Job metrics: [{'mean': 1.0}]
  One reward key across the job -> one metric, named after the
  metric type (mean), not after anything the task chose.

============================================================
Step 3: Named Dimensions (reward.json)
============================================================

  $ harbor run -p tasks/reward-json -a oracle -y

    ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
    ┃ Trials ┃ Exceptions ┃ Length ┃ Sections ┃ Title ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
    │      1 │          0 │  1.000 │    1.000 │ 1.000 │
    └────────┴────────────┴────────┴──────────┴───────┘

  Rewards recorded on the trial:
    sections   1.00
    title      1.00
    length     1.00

  Job metrics: [{'length': 1.0, 'sections': 1.0, 'title': 1.0}]
  Several reward keys -> the metric is computed PER KEY, so you can
  see which dimension an agent is failing, not just that it failed.

============================================================
Step 4: Precedence -- reward.json Beats reward.txt
============================================================

  Files the verifier left behind:
    reward.txt   0.00
    reward.json  {   "sections": 1.00,   "title": 1,   "length": 1,   "reward": 1.00 }

  Rewards Harbor actually recorded:
    sections   1.00
    title      1.00
    length     1.00
    reward     1.00

  reward.json won. The 0.00 in reward.txt was never read.
```

Notice the summary table in Step 3 grew a column per reward dimension — Harbor renders whatever names your verifier emitted.

## Key Takeaways

- Harbor always stores rewards as a dict; `reward.txt` is the one-dimensional special case, always keyed `"reward"`
- `reward.json` holds any `{name: number}` map — use it as soon as you measure more than one thing
- Metrics aggregate per key when several keys exist, so named dimensions survive all the way to the job summary
- Always emit a `"reward"` roll-up next to your dimensions, or `min_reward`, `harbor analyze`, and `harbor check` have nothing to read
- When both files exist, `reward.json` wins and `reward.txt` is dead code — the docs say otherwise and are wrong
- `[verifier.env]` uses `${VAR}` / `${VAR:-default}` templating and makes runs interactive; pass `-y` in scripts

## Next Steps

Continue to [LLM-as-a-Judge from Scratch](../lesson-2-llm-judge/), where the thing being graded is open-ended prose that no `grep` can score.
