# Custom Criteria & Multi-Dimensional Rewards

**Duration:** 45-55 minutes

## Overview

The built-in criteria cover files, commands, and structured data — but not "does the agent's `word_count()` function actually work?" This lesson covers writing your own criteria, splitting `tests/` into separately named reward dimensions, aggregating them with `reward.toml`, and finally comparing two candidate verifiers against the same workspace to see how much the *verifier* decides the score.

## Prerequisites

- Completed [RewardKit Judge Criteria](../lesson-4-judge-criteria/)
- Docker installed and running
- **LiteLLM gateway running** — `cd infra && docker compose up -d litellm`

## Concepts

### Directories are dimensions

Every **subdirectory** of `tests/` becomes its own named reward:

```
tests/
  test.sh
  criteria.py                shared custom criteria  (NOT a dimension)
  reward.toml                aggregation config      (NOT a dimension)
  correctness/functions.py -> reward "correctness"
  structure/files.py       -> reward "structure"
  quality/quality.toml     -> reward "quality"
```

The two root files are excluded for different reasons:

- **`criteria.py`** — a root-level `.py` is imported first *only* so subdirectories can call what it defines. It is never registered as its own reward.
- **`reward.toml`** — a `.toml` without a `[judge]` table is reward *configuration*, not a rubric. This is precisely why a rubric must have both `[judge]` and `[[criterion]]` to be recognized as one.

A dimension can mix kinds: drop a `.py` file into `quality/` next to `quality.toml` and that dimension gets both a programmatic and a judged reward, combined by their `reward_weight`.

### Three ways to write a criterion

**1. Zero-parameter — defining it registers it.**

```python
@criterion
def top_word_correct(workspace: Path) -> bool:
    ...
```

**2. Parameterized — defining it registers nothing.** RewardKit cannot guess your arguments, so you must call it. The `description` is `str.format`-ed with what you passed, giving each call a readable name in `reward-details.json`:

```python
@criterion(description="textstats.py defines at least {n} public functions")
def defines_n_functions(workspace: Path, n: int) -> bool:
    ...

rk.defines_n_functions(3, weight=2.0)
```

Forget the call and RewardKit tells you:

```
UserWarning: Criterion 'defines_n_functions' was defined with @criterion
but never called.
```

**3. Shared — defined once at the root, callable from any dimension.**

```python
# tests/criteria.py
@criterion(shared=True)
def word_count_correct(workspace: Path) -> float:
    ...

# tests/correctness/functions.py
from rewardkit import criteria
criteria.word_count_correct(weight=3.0)
```

Return a `float` instead of a `bool` to buy partial credit — these shared criteria return the fraction of test cases the agent's function passes.

### Test the function, not just the output file

The shared criteria here import the agent's `textstats` module and call `word_count()` on held-out inputs. That is a fundamentally better measurement than reading `results.json`, because **an output file can be hardcoded and a function cannot.** Step 5 makes this concrete.

### Two guardrails

**Calling a criterion function directly raises `TypeError`:**

```
TypeError: Call criteria through the rewardkit module: rk.stub(...) instead of stub(...)
```

The decorated object is a *factory*, not the check. Going through the module is what registers it against the current session instead of evaluating it on the spot.

**A non-shared criterion in a root file, when subdirectories exist, raises `ValueError`:**

```
ValueError: Root-level criteria 'orphaned' in /tests would be ignored in nested
layout (subdirectories exist). Either move them into a subdirectory or mark them
@criterion(shared=True).
```

Such a criterion would belong to no dimension and silently never run. RewardKit refuses rather than under-report.

Both are demonstrated live in `guardrails.py` — no container, no LLM.

### `reward.toml` aggregation

Each `[[reward]]` block **adds** one key, computed by aggregating the dimension scores. The per-dimension scores stay alongside it:

```toml
[[reward]]
name = "reward"
aggregation = "weighted_mean"

[[reward]]
name = "all_dimensions_passed"
aggregation = "all_pass"
```

Result:

```json
{"correctness": 1.0, "structure": 1.0, "quality": 1.0,
 "reward": 1.0, "all_dimensions_passed": 1.0}
```

Reporting both an aggregate and a gate means never having to choose between "how good was it" and "did it clear the bar". Dimensions are weighted by their summed `reward_weight`; the aggregation modes are the same five from Lesson 4.

### Comparing verifiers

`rewardkit` accepts several tests directories and grades the same workspace with each:

```bash
rewardkit local/v1 local/v2 --workspace local/workspace
```

## Step-by-Step

### Step 1: Directories are dimensions
### Step 2: Writing your own criteria
### Step 3: Two guardrails, demonstrated live
### Step 4: A reward with three dimensions (`tasks/pipeline/`)
### Step 5: Which verifier is better? (`local/`)

`local/workspace/` holds a deliberately, *subtly* broken implementation:

```python
def word_count(text: str) -> int:
    return len(text.split(" "))    # literal space, not whitespace
```

The sample file has no double spaces and no blank lines, so `results.json` comes out perfect. The function is still wrong — `"".split(" ")` is `[""]`, so an empty string counts as one word.

- **v1** grades the *output*: files exist, `results.json` holds the right numbers.
- **v2** grades the *function*: calls `word_count()` on four held-out inputs.

## Running the Lesson

```bash
cd infra && docker compose up -d litellm      # if not already running
cd tutorial/level-2-intermediate/module-08-grading-rewards/lesson-5-custom-criteria
uv sync
uv run python main.py
```

## Expected Output

```
    per-dimension (one per tests/ subdirectory):
      correctness             1.00
      quality                 1.00
      structure               1.00

    aggregated (added by tests/reward.toml):
      all_dimensions_passed   1.00
      reward                  1.00

  Per criterion, grouped by dimension:

    correctness  (programmatic)  ->  1.00
      word_count_correct                                1.00  x3
      unique_words_correct                              1.00  x3
      top_word_correct                                  1.00  x1
      json_key_equals:results.json                      1.00  x2
      json_key_equals:results.json                      1.00  x2
      json_key_equals:results.json                      1.00  x2

    quality  (llm)  ->  1.00
      documented                                        1.00  x1
      readability                                       1.00  x2
      handles_empty_input                               1.00  x2

    structure  (programmatic)  ->  1.00
      file_exists:textstats.py                          1.00  x1
      file_exists:analyze.py                            1.00  x1
      file_exists:results.json                          1.00  x1
      file_contains:analyze.py                          1.00  x1
      defines_n_functions:3                             1.00  x2

============================================================
Step 5: Which Verifier Is Better?
============================================================

    v1/reward: 1.0
    v2/reward: 0.75

    Comparison:
    ------------------------------
    reward      v1      v2    diff
    ------------------------------
    reward  1.0000  0.7500  +0.2500
    ------------------------------
```

Note `defines_n_functions:3` in the criteria table — the parameterized description carried the bound argument into the name, so a rubric with `defines_n_functions(3)` and `defines_n_functions(5)` produces two distinguishable rows.

**v1 gives the broken implementation full marks. v2 does not.** Same agent, same workspace, a `0.25` difference that comes entirely from the verifier. A verifier is a measurement instrument, and a lenient one reports a number you cannot trust — so compare verifiers the way you compare agents.

## Try It Yourself

Fix `local/workspace/textstats.py` to use `text.split()` and re-run. v2 rises to `1.0` and the two verifiers agree — which is what agreement is supposed to mean.

Then break it a different way: make `analyze.py` write a hardcoded `results.json` without calling `textstats` at all. v1 still says `1.0`.

## Key Takeaways

- Each `tests/` subdirectory becomes a named reward dimension; root `.py` and `reward.toml` do not
- Zero-parameter criteria register on definition; parameterized ones must be called
- Call criteria through the module (`rk.x` / `criteria.x`) — calling the function directly is a `TypeError`
- Root criteria in a nested layout must be `@criterion(shared=True)`, or discovery raises
- Return a `float` for partial credit rather than an all-or-nothing `bool`
- `[[reward]]` blocks add aggregated keys without replacing the dimensions
- Test the agent's *functions* against held-out inputs — output files can be hardcoded
- Two verifiers over the same workspace can differ by a lot; grade your verifier too

## Next Steps

Continue to [Judging the Process](../lesson-6-trajectory-judging/), which scores *how* the agent worked — and hardens the verifier against an agent that would rather edit the reward file than do the task.
