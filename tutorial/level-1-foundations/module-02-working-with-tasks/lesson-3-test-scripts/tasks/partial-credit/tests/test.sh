#!/bin/bash

# APPROACH 2: Partial-credit test
#
# Instead of pass/fail, this test awards partial credit.
# Each correct function earns 1/3 of the total reward.
# Final reward can be 0, 0.33, 0.67, or 1.0.

mkdir -p /logs/verifier

if [ ! -f /app/calculator.py ]; then
  echo "FAIL: /app/calculator.py does not exist"
  echo 0 >/logs/verifier/reward.txt
  exit 0
fi

PASSED=0
TOTAL=3

# Test add function
RESULT=$(python3 -c "from calculator import add; print(add(2, 3))" 2>/dev/null)
if [ "$RESULT" = "5" ]; then
  echo "PASS: add(2, 3) = 5"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: add(2, 3) expected 5, got '$RESULT'"
fi

# Test subtract function
RESULT=$(python3 -c "from calculator import subtract; print(subtract(10, 4))" 2>/dev/null)
if [ "$RESULT" = "6" ]; then
  echo "PASS: subtract(10, 4) = 6"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: subtract(10, 4) expected 6, got '$RESULT'"
fi

# Test multiply function
RESULT=$(python3 -c "from calculator import multiply; print(multiply(7, 8))" 2>/dev/null)
if [ "$RESULT" = "56" ]; then
  echo "PASS: multiply(7, 8) = 56"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: multiply(7, 8) expected 56, got '$RESULT'"
fi

# Calculate partial reward using awk for floating-point division
REWARD=$(awk "BEGIN {printf \"%.2f\", $PASSED / $TOTAL}")

echo ""
echo "Passed $PASSED / $TOTAL tests"
echo "Reward: $REWARD"
echo "$REWARD" >/logs/verifier/reward.txt
