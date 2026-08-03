#!/bin/bash

# Verify the FizzBuzz solution.
# Write a reward (0 or 1) to /logs/verifier/reward.txt.

mkdir -p /logs/verifier

# Check the script exists
if [ ! -f /app/fizzbuzz.py ]; then
  echo "FAIL: /app/fizzbuzz.py not found"
  echo 0 >/logs/verifier/reward.txt
  exit 0
fi

# Run the script and capture output
ACTUAL=$(python /app/fizzbuzz.py 2>/dev/null)

# Spot-check key positions
FAIL=0

check_line() {
  local line_num=$1
  local expected_val=$2
  local actual_val
  actual_val=$(echo "$ACTUAL" | sed -n "${line_num}p")
  if [ "$actual_val" != "$expected_val" ]; then
    echo "FAIL at line $line_num: expected '$expected_val', got '$actual_val'"
    FAIL=1
  fi
}

# Check total line count
ACTUAL_LINES=$(echo "$ACTUAL" | wc -l | tr -d ' ')
if [ "$ACTUAL_LINES" != "100" ]; then
  echo "FAIL: Expected 100 lines, got $ACTUAL_LINES"
  echo 0 >/logs/verifier/reward.txt
  exit 0
fi

# Check specific positions
check_line 1 "1"
check_line 3 "Fizz"
check_line 5 "Buzz"
check_line 15 "FizzBuzz"
check_line 30 "FizzBuzz"
check_line 97 "97"
check_line 99 "Fizz"
check_line 100 "Buzz"

if [ "$FAIL" -eq 0 ]; then
  echo "PASS: FizzBuzz output is correct"
  echo 1 >/logs/verifier/reward.txt
else
  echo 0 >/logs/verifier/reward.txt
fi
