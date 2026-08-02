#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/reverse.py ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: reverse.py not found"
  exit 0
fi

EXPECTED="dlrow olleh"
ACTUAL=$(python3 /home/user/reverse.py 2>/dev/null | tr -d '\n')

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "1.0" >/logs/verifier/reward.txt
  echo "PASS: String reversed correctly."
else
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: Expected '$EXPECTED', got '$ACTUAL'"
fi
