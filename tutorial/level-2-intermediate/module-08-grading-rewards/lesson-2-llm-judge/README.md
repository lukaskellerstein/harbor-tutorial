# LLM-as-a-Judge from Scratch

**Duration:** 40-50 minutes

## Overview

Lesson 1 graded with `grep` — the section is there or it isn't. This lesson grades a *funny poem*, which no string match can score. You will write a verifier that hands the agent's output to a model along with an explicit rubric, demands strict JSON back, validates it, and turns it into a multi-dimensional `reward.json`. You will also watch the judge disagree with itself on identical input, which is the single most important thing to understand about LLM grading.

## Prerequisites

- Completed [Rewards & the Verifier Contract](../lesson-1-reward-contract/)
- Harbor CLI installed
- Docker installed and running
- **LiteLLM gateway running** — `cd infra && docker compose up -d litellm` (see [infra/README.md](../../../../infra/README.md))

## Concepts

### When a judge is the right tool

A judge is expensive, slow, and non-deterministic. Reach for one only when the thing you are measuring genuinely resists a deterministic check. Four rules make the difference between a useful judge and an expensive random number generator:

**1. Write the rubric down.** "Is this good?" is not a gradable question. Each criterion must be independently answerable:

```python
RUBRIC = {
    "funny": "Is this poem actually funny? Consider wit, timing, and whether "
             "the joke lands, not merely whether it is competently written.",
    "on_topic": "Is the poem genuinely about debugging code -- bugs, stack "
                "traces, print statements, failing tests?",
}
```

**2. Run deterministic checks first.** The task also requires at least four lines. That is `len()`, not a judgement:

```python
def deterministic_checks(poem: str) -> dict[str, float]:
    lines = [line for line in poem.splitlines() if line.strip()]
    return {"line_count": 1.0 if len(lines) >= 4 else 0.0}
```

Never spend an LLM call on a question `len()` can answer. It costs money, adds latency, and adds variance to a measurement that had none.

**3. Demand structured output, then validate it.** Ask for strict JSON schema, and still check what comes back:

```python
class CriterionScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
```

A model that returns `7.5` on a 0–1 scale must fail loudly. Without the `ge`/`le` bounds it would silently inflate your reward and every downstream metric.

**4. Never swallow judge errors into a 0.0.** If the API times out and you record `0.0`, a broken judge and a terrible submission become indistinguishable — and your dataset now contains a lie:

```python
except Exception as exc:
    print(f"Judge call failed: {exc}", file=sys.stderr)
    raise    # fail the verifier; do not fake a score
```

### Wiring credentials without committing them

`task.toml` names the variables; your shell supplies the values:

```toml
[verifier.env]
OPENAI_BASE_URL = "${LITELLM_BASE_URL:-http://host.docker.internal:4000/v1}"
OPENAI_API_KEY  = "${LITELLM_MASTER_KEY:-sk-litellm-master}"
JUDGE_MODEL     = "${JUDGE_MODEL:-gemma-large}"
```

Two things worth noticing:

- **`host.docker.internal`** is the host machine as seen from inside the container. `localhost` inside a Harbor container is the container itself, not your laptop. Docker Desktop on macOS and Windows resolves this name automatically; on Linux you need `--add-host=host.docker.internal:host-gateway`.
- **`JUDGE_MODEL` is a variable, not a literal.** Swapping judges is an environment change, never a code change. That property is the entire reason the gateway exists.

Harbor's verifier network defaults to `public` (`NetworkMode.PUBLIC` in `src/harbor/models/task/config.py`), so no extra configuration is needed to reach the gateway.

### PEP 723: dependencies next to the script

The judge declares what it needs inline:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.60",
#   "pydantic>=2.9",
# ]
# ///
```

`uv run` reads that block, builds a throwaway environment, and runs the script — so `tests/test.sh` is one line and the task's Dockerfile never learns about `openai`:

```bash
#!/bin/bash
uv run /tests/llm_judge.py
```

The image is `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, which ships `uv` preinstalled.

## Step-by-Step

### Step 1: When you need a judge
`main.py` states the four rules before any code runs.

### Step 2: The judge script
Walks `tests/llm_judge.py` — rubric, schema, and the `[verifier.env]` wiring.

### Step 3: Judge a poem
Runs the task with the `oracle` agent (so the poem is fixed and only the *judging* varies) and prints both the recorded rewards and everything the judge printed. That output is captured by Harbor at `verifier/test-stdout.txt` — the first place to look when a score seems wrong, because the reasoning is right there.

### Step 4: Judge the same poem again
Identical input, identical rubric, second opinion.

### Step 5: Compare the two runs
The point of the lesson.

## Running the Lesson

```bash
cd infra && docker compose up -d litellm      # if not already running
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-2-llm-judge
uv sync
uv run python main.py
```

Two judged trials against `gemma-large` (OpenRouter's free gemma-4 tier by default) cost effectively nothing.

## Expected Output

```
============================================================
Checking Prerequisites
============================================================
  Docker CLI:      [OK]
  Docker running:  [OK]
  Harbor CLI:      [OK]
  LiteLLM gateway: [OK]

...

    ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
    ┃ Trials ┃ Exceptions ┃ Funny ┃ Line_Count ┃ On_Topic ┃ Reward ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
    │      1 │          0 │ 0.800 │      1.000 │    1.000 │  0.933 │
    └────────┴────────────┴───────┴────────────┴──────────┴────────┘

  Rewards recorded on the trial:
    line_count   1.00
    funny        0.80
    on_topic     1.00
    reward       0.93

  What the judge printed (captured at verifier/test-stdout.txt):
    deterministic: {'line_count': 1.0}
    funny: 0.80 -- The joke about git-blaming oneself is a relatable programmer
                   trope that provides a clever punchline.
    on_topic: 1.00 -- The poem directly addresses debugging through print
                      statements, stack traces, and failing tests.
    wrote /logs/verifier/reward.json: {'line_count': 1.0, 'funny': 0.8,
                                       'on_topic': 1.0, 'reward': 0.933}

============================================================
Step 5: Judges Disagree With Themselves
============================================================

  dimension      run 1   run 2   delta
  ------------ ------- ------- -------
  line_count      1.00    1.00   +0.00
  funny           0.70    0.80   +0.10
  on_topic        1.00    1.00   +0.00
  reward          0.90    0.93   +0.03

  Same poem, same rubric, scores moved by up to 0.10.
```

Your exact numbers will differ — that is the finding, not a defect. Note which rows moved: `line_count` and `on_topic` held steady while `funny` drifted. Judgements that are nearly factual are stable; genuinely subjective ones are not.

**Consequences for how you use judged scores:**

- Do not gate on them. A `min_reward = 0.8` on a dimension that swings ±0.1 fails builds at random.
- Compare agents against each other on the same rubric rather than against an absolute threshold.
- Average over several trials before believing a difference is real.
- Keep hard pass/fail gates on the deterministic dimensions.

## Troubleshooting

**`LiteLLM gateway: [UNREACHABLE]`** — start it with `cd infra && docker compose up -d litellm`, then confirm: `curl http://localhost:4000/health/liveliness`.

**Judge call fails with a connection error inside the container** — the container cannot see your host. Verify `host.docker.internal` resolves there; on Linux you must add the host-gateway mapping explicitly.

**The judge returns prose instead of JSON** — the model behind `gemma-large` does not support strict JSON schema. Point at a stronger one for the run: `JUDGE_MODEL=gpt-mini uv run python main.py`.

## Key Takeaways

- A judge is a verifier that happens to call a model — the reward contract is unchanged
- Write the rubric down; one criterion per gradable question
- Run every deterministic check first, and never spend an LLM call on what `len()` can answer
- Demand strict JSON schema and validate the result — bounds-check scores rather than trusting them
- Raise on judge errors; scoring them `0.0` makes a broken judge look like a bad agent
- Credentials and model choice live in `[verifier.env]`, so swapping judges never touches code
- Judged scores are noisy: compare agents, average trials, and keep hard gates on deterministic checks

## Next Steps

Continue to [RewardKit: Programmatic Criteria](../lesson-3-rewardkit-basics/), which replaces both this 150-line judge and Lesson 1's bash verifiers with declarative criteria files.
