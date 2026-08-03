#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/count_words.py ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: count_words.py not found"
  exit 0
fi

EXPECTED="9"
ACTUAL=$(python3 /home/user/count_words.py 2>/dev/null)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "1.0" >/logs/verifier/reward.txt
  echo "PASS: Word count is correct."
else
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: Expected $EXPECTED, got $ACTUAL"
fi
