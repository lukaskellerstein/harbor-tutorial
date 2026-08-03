#!/bin/bash
if [ ! -f /app/report.txt ]; then
  echo "FAIL: /app/report.txt does not exist"
  echo 0 >/logs/verifier/reward.txt
  exit 0
fi

EXPECTED_TOTAL="Total words: 11"
EXPECTED_UNIQUE="Unique words: 8"

ACTUAL=$(cat /app/report.txt)

if echo "$ACTUAL" | grep -q "$EXPECTED_TOTAL" && echo "$ACTUAL" | grep -q "$EXPECTED_UNIQUE"; then
  echo "PASS: report.txt has correct word counts"
  echo 1 >/logs/verifier/reward.txt
else
  echo "FAIL: report.txt has incorrect content"
  echo "Expected to contain:"
  echo "  $EXPECTED_TOTAL"
  echo "  $EXPECTED_UNIQUE"
  echo "Actual:"
  echo "  $ACTUAL"
  echo 0 >/logs/verifier/reward.txt
fi
