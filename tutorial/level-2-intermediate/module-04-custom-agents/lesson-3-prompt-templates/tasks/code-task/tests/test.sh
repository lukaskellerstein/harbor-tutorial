#!/bin/bash
# Test: verify fibonacci.py exists and produces correct output

if [ ! -f /home/user/fibonacci.py ]; then
  echo "FAIL: fibonacci.py not found"
  echo "0.0" >/logs/verifier/reward.txt
  exit 0
fi

OUTPUT=$(python3 /home/user/fibonacci.py 2>/dev/null)
EXPECTED="[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]"

if [ "$OUTPUT" = "$EXPECTED" ]; then
  echo "PASS: fibonacci.py produces correct output"
  echo "1.0" >/logs/verifier/reward.txt
else
  echo "FAIL: expected '$EXPECTED', got '$OUTPUT'"
  echo "0.0" >/logs/verifier/reward.txt
fi
