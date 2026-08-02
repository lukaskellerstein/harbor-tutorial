#!/bin/bash
# Test: check that output.txt contains the reversed string

EXPECTED="krowemarF robraH"

if [ -f /workspace/output.txt ]; then
  content=$(cat /workspace/output.txt | tr -d '\n')
  if [ "$content" = "$EXPECTED" ]; then
    echo "PASS: output.txt contains the correct reversed string"
    echo "1.0" >/logs/verifier/reward.txt
  else
    echo "FAIL: incorrect output"
    echo "Expected: $EXPECTED"
    echo "Got:      $content"
    echo "0.0" >/logs/verifier/reward.txt
  fi
else
  echo "FAIL: output.txt not found"
  echo "0.0" >/logs/verifier/reward.txt
fi
