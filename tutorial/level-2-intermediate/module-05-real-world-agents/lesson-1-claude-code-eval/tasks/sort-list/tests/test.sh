#!/bin/bash
EXPECTED="3
8
17
21
42
56
99"

if [ ! -f /app/sorted.txt ]; then
  echo "FAIL: /app/sorted.txt does not exist"
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

ACTUAL=$(cat /app/sorted.txt)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "PASS: sorted.txt contains correctly sorted numbers"
  echo 1 > /logs/verifier/reward.txt
else
  echo "FAIL: sorted.txt contains incorrect output"
  echo "Expected:"
  echo "$EXPECTED"
  echo "Actual:"
  echo "$ACTUAL"
  echo 0 > /logs/verifier/reward.txt
fi
