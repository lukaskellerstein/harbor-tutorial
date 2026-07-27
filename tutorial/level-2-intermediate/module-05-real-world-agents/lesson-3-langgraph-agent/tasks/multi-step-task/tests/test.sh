#!/bin/bash
REWARD=0

# Check config.json exists and has correct content
if [ ! -f /app/project/config.json ]; then
  echo "FAIL: /app/project/config.json does not exist"
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

# Check output.txt exists
if [ ! -f /app/project/output.txt ]; then
  echo "FAIL: /app/project/output.txt does not exist"
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

# Check output.txt has exactly 5 lines with correct content
EXPECTED="Entry 1
Entry 2
Entry 3
Entry 4
Entry 5"

ACTUAL=$(cat /app/project/output.txt)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "PASS: output.txt contains correct entries"
  echo 1 > /logs/verifier/reward.txt
else
  echo "FAIL: output.txt has incorrect content"
  echo "Expected:"
  echo "$EXPECTED"
  echo "Actual:"
  echo "$ACTUAL"
  echo 0 > /logs/verifier/reward.txt
fi
