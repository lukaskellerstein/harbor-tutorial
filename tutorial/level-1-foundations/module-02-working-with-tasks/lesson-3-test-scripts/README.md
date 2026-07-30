# Writing Test Scripts

**Duration:** 30-40 minutes

## Overview

The test script is the most important part of a Harbor task -- it determines the reward and ultimately measures agent performance. In this lesson you will learn three approaches to writing test scripts: binary pass/fail, partial-credit scoring, and pytest-based testing with CTRF reporting.

## Prerequisites

- Completed lesson: [Scaffolding a Task](../lesson-2-create-a-task/)
- Harbor CLI installed
- Docker installed and running

## Concepts

### The Reward Contract

Every test script must follow one simple contract:

**Write a floating-point number (0 to 1) to `/logs/verifier/reward.txt`.**

This is how Harbor measures whether an agent succeeded. The test script runs inside the same container where the agent worked, so it has access to everything the agent created or modified.

```bash
mkdir -p /logs/verifier
echo 1 > /logs/verifier/reward.txt    # Full success
echo 0 > /logs/verifier/reward.txt    # Failure
echo 0.5 > /logs/verifier/reward.txt  # Partial credit
```

### Three Testing Approaches

| Approach | Reward Values | Best For |
|----------|--------------|----------|
| Binary test | 0 or 1 | Simple, clear-cut tasks |
| Partial credit | 0 to 1 (fractional) | Tasks with multiple criteria |
| Pytest + CTRF | 0 or 1 (per pytest result) | Complex tasks with many test cases |

### Important Test Script Rules

1. **Always `mkdir -p /logs/verifier`** before writing the reward file
2. **Exit with code 0** even when the test fails -- let the reward value communicate the result, not the exit code
3. **Print diagnostic output** -- it goes to `/logs/verifier/test-stdout.txt` and helps with debugging
4. **Test outcomes, not methods** -- check what the agent produced, not how it got there

## Step-by-Step

### Step 1: Binary Test (Pass/Fail)

The simplest approach. Check a single condition and write 0 or 1.

**Task:** `tasks/binary-test/` -- Create a file with specific content.

**test.sh pattern:**

```bash
#!/bin/bash
mkdir -p /logs/verifier

if [ -f /app/greeting.txt ]; then
    ACTUAL=$(cat /app/greeting.txt | tr -d '\n')
    if [ "$ACTUAL" = "Hello, Harbor!" ]; then
        echo 1 > /logs/verifier/reward.txt
    else
        echo 0 > /logs/verifier/reward.txt
    fi
else
    echo 0 > /logs/verifier/reward.txt
fi
```

Use this for tasks with a clear right/wrong answer.

### Step 2: Partial-Credit Test

Award fractional credit based on how many criteria the agent satisfied.

**Task:** `tasks/partial-credit/` -- Implement three calculator functions.

**test.sh pattern:**

```bash
#!/bin/bash
mkdir -p /logs/verifier

PASSED=0
TOTAL=3

# Test each function independently
RESULT=$(python3 -c "from calculator import add; print(add(2, 3))" 2>/dev/null)
if [ "$RESULT" = "5" ]; then PASSED=$((PASSED + 1)); fi

# ... test more functions ...

# Calculate fractional reward
REWARD=$(awk "BEGIN {printf \"%.2f\", $PASSED / $TOTAL}")
echo $REWARD > /logs/verifier/reward.txt
```

This gives a reward of 0, 0.33, 0.67, or 1.00 depending on how many functions the agent implemented correctly.

### Step 3: Pytest-Based Test with CTRF

Use pytest for structured testing with rich output. This is Harbor's default when you run `harbor task init`.

**Task:** `tasks/pytest-test/` -- Implement string utility functions.

**test.sh pattern:**

```bash
#!/bin/bash
mkdir -p /logs/verifier

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

uvx \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_state.py -rA

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

The CTRF plugin produces a structured JSON report alongside the reward, which Harbor stores in the trial output for later analysis.

### Step 4: Run All Three

The lesson script runs each task with the oracle agent and displays the results, so you can compare how each approach works in practice.

## Running the Lesson

```bash
cd tutorial/level-1-foundations/module-02-working-with-tasks/lesson-3-test-scripts
uv sync
uv run python main.py
```

## Expected Output

```text
########################################################
#          HARBOR TUTORIAL - Module 2, Lesson 3         #
#          Writing Test Scripts                         #
########################################################

============================================================
Step 1: How Test Scripts Work
============================================================
  Every Harbor test script must do ONE thing:
    Write a number (0 to 1) to /logs/verifier/reward.txt

============================================================
Step 2: Approach 1 -- Binary Test (Pass/Fail)
============================================================
  ... (test.sh contents displayed) ...
  Running: harbor run -p tasks/binary-test -a oracle
  ...
  Expected reward: 1
  Trial completed successfully.

============================================================
Step 3: Approach 2 -- Partial-Credit Test
============================================================
  ... (test.sh contents displayed) ...
  Running: harbor run -p tasks/partial-credit -a oracle
  ...
  Expected reward: 1.00 (0.33 per function)
  Trial completed successfully.

============================================================
Step 4: Approach 3 -- Pytest-Based Test with CTRF
============================================================
  ... (test.sh contents displayed) ...
  Running: harbor run -p tasks/pytest-test -a oracle
  ...
  Expected reward: 1
  Trial completed successfully.

============================================================
Summary
============================================================
  Three approaches: Binary, Partial credit, Pytest + CTRF
  All share the same contract: write float to /logs/verifier/reward.txt
```

## Key Takeaways

- Every test script must write a float (0-1) to `/logs/verifier/reward.txt`
- Binary tests are simplest: check one condition, write 0 or 1
- Partial-credit tests count successes and calculate a fractional reward
- Pytest-based tests (Harbor's default) provide structured reporting via CTRF
- Always exit test.sh with code 0 -- use the reward value, not the exit code, to signal results
- Print diagnostic output; it is captured in the trial logs for debugging

## Next Steps

Continue to the next lesson: [Debugging with Interactive Environments](../lesson-4-interactive-env/) to learn how to enter a task container and debug interactively.
