#!/bin/bash
# Test: verify the greeter binary was run and output captured

REWARD_FILE="/logs/verifier/reward.txt"

if [ -f /app/greeting.txt ] && grep -q "multi-stage" /app/greeting.txt; then
  echo "PASS: greeting.txt exists and contains expected output"
  echo "1" >"$REWARD_FILE"
else
  echo "FAIL: greeting.txt missing or does not contain expected output"
  echo "0" >"$REWARD_FILE"
fi
