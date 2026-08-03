#!/bin/bash
# Test: check that greeting.txt exists and contains the correct greeting

EXPECTED="Hello, Harbor!"

if [ -f /workspace/greeting.txt ]; then
  content=$(cat /workspace/greeting.txt | tr -d '\n')
  if [ "$content" = "$EXPECTED" ]; then
    echo "PASS: greeting.txt contains '$EXPECTED'"
    echo "1.0" >/logs/verifier/reward.txt
  else
    echo "FAIL: incorrect content"
    echo "Expected: $EXPECTED"
    echo "Got:      $content"
    echo "0.0" >/logs/verifier/reward.txt
  fi
else
  echo "FAIL: greeting.txt not found"
  echo "0.0" >/logs/verifier/reward.txt
fi
