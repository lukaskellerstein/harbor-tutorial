#!/bin/bash
# Test: verify output.txt exists and contains the expected text

EXPECTED="Hello from Harbor"
ACTUAL=$(cat /home/user/output.txt 2>/dev/null)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "PASS: output.txt contains the expected text"
  echo "1.0" >/logs/verifier/reward.txt
else
  echo "FAIL: expected '$EXPECTED', got '$ACTUAL'"
  echo "0.0" >/logs/verifier/reward.txt
fi
