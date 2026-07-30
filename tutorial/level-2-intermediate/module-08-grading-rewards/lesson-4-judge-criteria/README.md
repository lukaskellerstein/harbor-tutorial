# RewardKit Judge Criteria

**Duration:** 40-50 minutes

## Overview

Lesson 2 built an LLM judge by hand: 150 lines of Python for two criteria, plus schema construction, validation, and error handling you now own. This lesson replaces all of it with a TOML rubric and no Python at all — then shows two things that decide your scores more than the rubric text does: which aggregation mode you pick, and which model does the judging.

## Prerequisites

- Completed [RewardKit: Programmatic Criteria](../lesson-3-rewardkit-basics/)
- Completed [LLM-as-a-Judge from Scratch](../lesson-2-llm-judge/)
- Docker installed and running
- **LiteLLM gateway running** — `cd infra && docker compose up -d litellm`

## Concepts

### A rubric is a TOML file

RewardKit treats a `.toml` under `tests/` as a rubric **if and only if it has both a `[judge]` table and at least one `[[criterion]]`**. Anything else is ignored — which is how `tests/reward.toml` (Lesson 5) coexists in the same directory without confusion.

```toml
[judge]
judge = "openai/gemma-large"
files = ["/app/poem.txt"]
mode = "batched"

[[criterion]]
name = "on_topic"
description = "Is the poem genuinely about debugging code?"
type = "binary"
weight = 1.0
```

Discovery is identical to a `.py` criteria file: a rubric is just another kind of criteria file.

### Output formats

| `type` | Judge answers | Normalized to |
|--------|---------------|---------------|
| `binary` | yes / no | `1.0` / `0.0` |
| `likert` (+ `points`) | `1..N` | `(raw - 1) / (points - 1)` |
| `numeric` (+ `min`/`max`) | a free score | scaled into the range |

`reward-details.json` keeps both: `raw` is what the judge said, `value` is the normalized score. That is what makes a surprising number diagnosable.

### `files` decides what the judge can see

Without `files`, the judge grades nothing. Two modes control how the call is made:

- `mode = "batched"` (default) — one call scoring every criterion. Cheap.
- `mode = "individual"` — one call per criterion. Costlier, but **required** if any criterion sets its own `files`. Combining per-criterion `files` with `batched` raises:

  ```text
  ValueError: per-criterion 'files' requires the judge to use mode = "individual"
  ```

### `negate` — and the naming trap that comes with it

`negate = true` lets you ask the natural question and have RewardKit flip the answer, instead of writing double negatives that make judges guess.

But **the criterion `name` is part of the judge's prompt.** RewardKit renders each criterion as (`rewardkit/judges.py:_build_criteria_block`):

```text
- 'contains_profanity': Does the poem contain profanity or slurs? (score: yes/no)
```

Name the criterion after the *outcome you want* rather than the *question you asked*, and you hand the judge a contradiction. This exact rubric, with the criterion named `no_profanity`:

```text
no_profanity  ->  0.00   (raw='yes', weight=1.0)  [negated]
    The poem contains no profanity or slurs.
```

A score of `0.00` on a poem the judge just described as clean. The judge answered the *label* (`yes, no profanity`), `negate` flipped the already-correct answer, and the reward silently dropped. Renaming it to `contains_profanity` — matching the question — fixes it:

```text
contains_profanity  ->  1.00   (raw='no', weight=1.0)  [negated]
    The poem contains no profanity.
```

**Name criteria after the question, not the desired outcome.**

### Aggregation is a real decision

`[scoring] aggregation` turns per-criterion scores into one reward:

| Mode | Rule |
|------|------|
| `weighted_mean` (default) | weighted average of every criterion |
| `all_pass` | `1.0` only if every criterion scored **> 0** |
| `any_pass` | `1.0` if any criterion scored > 0 |
| `threshold` | `1.0` if the weighted mean ≥ `threshold` (default `0.5`) |
| `required_pass` | `all_pass`, ignoring `optional = true` criteria |

`main.py` takes the scores the judge actually produced and runs all five over them, using RewardKit's own `aggregate_scores` rather than a reimplementation.

> **`all_pass` is weaker than it looks on graded criteria.** It asks "is every criterion **> 0**?", not "is every criterion `1.0`?". A likert answer of 2/5 normalizes to `0.25` and sails through. In the sample run below, `weighted_mean` says `0.59` and `all_pass` says `1.00` on the same judgement. `all_pass` is a strong gate over *binary* criteria and a nearly meaningless one over likert and numeric; a mixed rubric under `all_pass` mostly measures its binary criteria.

### Reaching an OpenAI-compatible gateway

```toml
[verifier.env]
OPENAI_BASE_URL = "${LITELLM_BASE_URL:-http://host.docker.internal:4000/v1}"
OPENAI_API_BASE = "${LITELLM_BASE_URL:-http://host.docker.internal:4000/v1}"
OPENAI_API_KEY  = "${LITELLM_MASTER_KEY:-sk-litellm-master}"
LITELLM_DROP_PARAMS = "1"
```

`LITELLM_DROP_PARAMS` is **required**, and the reason is not obvious. RewardKit's `LLMJudge` always sends `reasoning_effort` (it defaults to `"medium"`). The litellm *client* inside the container validates parameters per provider before sending anything, and the `openai/` provider rejects it:

```text
litellm.UnsupportedParamsError: openai does not support parameters:
['reasoning_effort'], for model=gemma-large
```

The `drop_params: true` in the gateway's own config does **not** help — that is server-side, and the request never leaves the container. `LITELLM_DROP_PARAMS` sets `litellm.drop_params` in the client instead.

### Swapping the judge without editing the rubric

`REWARDKIT_JUDGE` is read *before* the rubric's `judge =` line (`rewardkit/runner.py:_build_judge_from_toml`):

```bash
REWARDKIT_JUDGE=openai/gpt-mini uv run python main.py    # for one run
rewardkit /tests --judge openai/gemma-local              # outside Harbor
```

`REWARDKIT_MODEL` does the same for an agent judge's inner model. This matters more than it looks: judge choice is the biggest single lever on your scores, and keeping it in the environment means re-grading an entire benchmark with a stronger judge takes zero diffs.

### Agent judges

Set `judge = "claude-code"` (or `"codex"`) and the judge gets a filesystem instead of a fixed file list — it can explore the workspace, run things, and grade what it finds. With MCP servers it can drive a browser:

```toml
[judge]
judge = "claude-code"
isolated = true

[[judge.mcp_servers]]
name = "playwright"
transport = "stdio"
command = "npx"
args = ["@playwright/mcp@latest", "--headless"]
```

That costs real money per trial, so this lesson ships the config without running it.

## Step-by-Step

### Step 1: Rubric anatomy

Prints `tests/judge.toml` in full and covers formats, flags, and the naming trap.

### Step 2: Judging against the rubric

One trial with the `oracle` agent, then the per-criterion breakdown with the judge's reasoning.

### Step 3: Aggregation changes everything

The same scores through all five modes.

### Step 4: Swapping the judge

`REWARDKIT_JUDGE`, `REWARDKIT_MODEL`, and agent judges.

## Running the Lesson

```bash
cd infra && docker compose up -d litellm      # if not already running
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-4-judge-criteria
uv sync
uv run python main.py
```

## Expected Output

```text
  reward.json:
    reward   0.59

  Per-criterion, from reward-details.json:

    on_topic  ->  1.00   (raw='yes', weight=1.0)
        The poem explicitly discusses debugging through print statements,
        stack traces, and tests failing ('tests went pop').

    humor  ->  0.50   (raw=3, weight=3.0)
        The humor is relatable for developers (ignoring stack traces,
        git-blaming oneself), though the structure and rhymes are fairly standard.

    originality  ->  0.30   (raw=0.3, weight=2.0)
        Uses common developer imagery like print statements, stack traces,
        and git-blame, which borders on stock cliches.

    contains_profanity  ->  1.00   (raw='no', weight=1.0)  [negated]
        The poem contains no profanity.

============================================================
Step 3: Aggregation Changes Everything
============================================================

  Taking the exact scores the judge just produced:
    on_topic            1.00  (weight 1.0)
    humor               0.50  (weight 3.0)
    originality         0.30  (weight 2.0)
    contains_profanity  1.00  (weight 1.0)

  ...and running each aggregation mode over them:

    aggregation       reward   meaning
    ---------------- -------   ----------------------------------------
    weighted_mean       0.59   weighted average of every criterion
    all_pass            1.00   1.0 only if EVERY criterion scored > 0
    any_pass            1.00   1.0 if ANY criterion scored > 0
    threshold           1.00   1.0 if the weighted mean >= threshold (0.5)
    required_pass       1.00   all_pass, ignoring optional=true criteria
```

Judged scores drift between runs — see Lesson 2. Your `humor` and `originality` numbers will differ; `on_topic` and `contains_profanity` should be stable, because they are nearly factual.

## Troubleshooting

**`RewardFileNotFoundError` with `UnsupportedParamsError` in the verifier log** — `LITELLM_DROP_PARAMS` is missing from `[verifier.env]`. See above.

**A criterion scores the opposite of its reasoning** — you have a `negate` whose criterion name contradicts its description. Rename the criterion after the question.

**The judge returns prose instead of JSON** — the backing model does not support strict JSON schema. `REWARDKIT_JUDGE=openai/gpt-mini uv run python main.py`.

## Key Takeaways

- A rubric is a TOML with `[judge]` + `[[criterion]]`; anything else in `tests/` is ignored
- `binary` / `likert(points)` / `numeric(min,max)` all normalize to 0–1, and `reward-details.json` keeps the raw answer alongside
- `files` decides what the judge sees; per-criterion `files` requires `mode = "individual"`
- **The criterion name is in the judge's prompt** — name it after the question, especially with `negate`
- `all_pass` tests `> 0`, not `== 1.0`, so it barely constrains likert and numeric criteria
- `LITELLM_DROP_PARAMS=1` is required to reach an OpenAI-compatible gateway, because RewardKit always sends `reasoning_effort`
- `REWARDKIT_JUDGE` overrides the rubric, so re-grading with a different judge takes no diffs

## Next Steps

Continue to [Custom Criteria & Multi-Dimensional Rewards](../lesson-5-custom-criteria/), where you write your own criterion functions and split `tests/` into separately named reward dimensions.
