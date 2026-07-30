# Metrics & Aggregation

**Duration:** 30-40 minutes

## Overview

After running an evaluation, Harbor produces a per-trial reward (a number between 0 and 1) for every task. Raw rewards alone do not tell you much -- you need aggregate metrics to compare agents, spot weaknesses, and track progress. This lesson teaches you how to compute and interpret key evaluation metrics: mean reward, pass rate, pass@1, and per-difficulty breakdowns.

## Prerequisites

- Completed Level 1 and Level 2 modules (familiarity with tasks, datasets, and running evaluations)
- Docker installed and running
- Harbor installed (`uv tool install harbor`)

## Concepts

### Rewards

Harbor's verifier runs a test script after each trial and writes a reward between 0.0 and 1.0 to `/logs/verifier/reward.txt` inside the container. This reward is stored in the trial's `result.json` file under `verifier_result.rewards.reward`.

- **0.0** -- the agent failed the task entirely
- **Between 0 and 1** -- partial credit (e.g., the agent got 3 of 4 sub-checks correct, yielding 0.75)
- **1.0** -- the agent solved the task perfectly

### Aggregate Metrics

From a set of per-trial rewards, you compute:

| Metric | Definition | Use Case |
|--------|-----------|----------|
| **Mean reward** | Average reward across all trials | Primary summary statistic |
| **Max reward** | Highest reward in the set | Best-case performance |
| **Min reward** | Lowest reward in the set | Worst-case performance |
| **Sum** | Total of all rewards | Ranking, quick comparison |
| **Pass rate** | Fraction of trials with reward > 0 | How often the agent makes any progress |
| **Pass@1** | Fraction of trials with reward == 1.0 | How often the agent fully solves tasks |

### Grouping by Metadata

Each task's `task.toml` contains metadata such as `difficulty`, `category`, and `tags`. By grouping results along these dimensions, you can identify where an agent excels (e.g., easy string tasks) and where it struggles (e.g., hard math tasks).

## Step-by-Step

### Step 1: Understanding Rewards

Rewards are the fundamental unit of evaluation in Harbor. Every test script must write a numeric value to `/logs/verifier/reward.txt`. Simple tests produce binary results (0.0 or 1.0), while more sophisticated tests can award partial credit by checking multiple conditions and computing a fractional score.

### Step 2: Exploring the Tasks

This lesson includes 4 tasks of varying difficulty:

| Task | Difficulty | Scoring |
|------|-----------|---------|
| `count-words` | easy | Binary (0 or 1) |
| `sort-numbers` | easy | Binary (0 or 1) |
| `csv-stats` | medium | Partial credit (4 sub-checks) |
| `matrix-multiply` | hard | Partial credit (2 row checks) |

### Step 3: Running the Evaluation

The lesson runs all 4 tasks using the oracle agent (which executes the reference `solution/solve.sh`). Since the oracle always produces perfect solutions, all rewards should be 1.0 -- confirming the tasks and tests are correct.

### Step 4: Parsing Results

Each trial writes a `result.json` file with this structure:

```json
{
  "task_name": "tutorial/metrics-count-words",
  "verifier_result": {"rewards": {"reward": 1.0}},
  "agent_info": {"name": "oracle", "version": "..."},
  ...
}
```

The lesson parses these files from the `jobs/` directory to extract per-trial rewards.

### Step 5: Computing Aggregate Metrics

With rewards in hand, we compute mean, max, min, sum, pass rate, and pass@1. These metrics give you a complete picture of agent performance at a glance.

### Step 6: Grouping by Difficulty

Using `tomllib` to read each task's `task.toml`, we map task names to their difficulty level and compute per-group metrics. This reveals whether an agent handles easy tasks but fails on hard ones -- a common and important finding.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-11-analysis-optimization/lesson-1-metrics
uv sync
uv run python main.py
```

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Level 3, Module 11         #
#          Lesson 1: Metrics & Aggregation              #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Docker:  [OK]
  Harbor:  [OK]

============================================================
Step 2: Understanding Evaluation Metrics
============================================================
  ...metrics explanation...

============================================================
Step 3: Our Evaluation Tasks
============================================================
  Task                    Difficulty  Description
  ------------------------ ----------  ------------------------------
  count-words             easy        Count words in a text file
  sort-numbers            easy        Sort numbers from a file
  csv-stats               medium      Compute stats from CSV data
  matrix-multiply         hard        Multiply two matrices

============================================================
Step 4: Running the Evaluation
============================================================
  Running: harbor run -p tasks -a oracle --delete -o jobs
  ...harbor output...

============================================================
Step 5: Parsing Results
============================================================
  ...result.json structure...

============================================================
Step 6: Per-Task Results
============================================================
  Task                                     Difficulty     Reward  Status
  ---------------------------------------- ------------ --------  -------
  tutorial/metrics-count-words             easy             1.00  [PASS]
  tutorial/metrics-sort-numbers            easy             1.00  [PASS]
  tutorial/metrics-csv-stats               medium           1.00  [PASS]
  tutorial/metrics-matrix-multiply         hard             1.00  [PASS]

============================================================
Step 7: Aggregate Metrics
============================================================
  Total trials:    4
  Mean reward:     1.0000
  Max reward:      1.00
  Min reward:      1.00
  Sum of rewards:  4.00
  Pass rate:       100.0%  (reward > 0)
  Pass@1:          100.0%  (reward == 1.0)

============================================================
Step 8: Metrics Grouped by Difficulty
============================================================
  Difficulty    Count     Mean  Pass Rate   Pass@1
  ------------ ------ -------- ---------- --------
  easy              2   1.0000     100.0%   100.0%
  medium            1   1.0000     100.0%   100.0%
  hard              1   1.0000     100.0%   100.0%

============================================================
Step 9: Comparing Agents and Models
============================================================
  ...comparison guidance...

============================================================
Summary
============================================================
  ...key takeaways...
```

## Key Takeaways

- Rewards are per-trial scores between 0 (fail) and 1 (pass), with partial credit supported.
- Mean reward is the primary metric for summarizing agent performance across a dataset.
- Pass@1 (fraction with reward == 1.0) measures strict correctness and is commonly reported in benchmarks.
- Grouping results by task metadata (difficulty, category) reveals an agent's strengths and weaknesses.
- Use `harbor view jobs` to interactively explore results in a web-based viewer.

## Next Steps

Proceed to the **trajectories** lesson to learn how to analyze agent trajectories -- the step-by-step record of what an agent did during a trial -- to understand not just whether it succeeded, but how.
