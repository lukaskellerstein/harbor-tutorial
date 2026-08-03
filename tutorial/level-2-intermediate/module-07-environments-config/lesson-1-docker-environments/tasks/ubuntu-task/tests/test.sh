#!/bin/bash
# Test: verify output.txt exists and contains Ubuntu version info

REWARD_FILE="/logs/verifier/reward.txt"

if [ -f /app/output.txt ] && grep -qi "ubuntu" /app/output.txt; then
  echo "PASS: output.txt exists and contains Ubuntu version info"
  echo "1" >"$REWARD_FILE"
else
  echo "FAIL: output.txt missing or does not contain Ubuntu info"
  echo "0" >"$REWARD_FILE"
fi
