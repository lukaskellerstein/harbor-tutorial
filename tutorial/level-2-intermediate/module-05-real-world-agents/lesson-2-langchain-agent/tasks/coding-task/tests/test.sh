#!/bin/bash
if [ ! -f /app/fibonacci.py ]; then
  echo "FAIL: /app/fibonacci.py does not exist"
  echo 0 >/logs/verifier/reward.txt
  exit 0
fi

OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '/app')
from fibonacci import fibonacci
print(fibonacci(10))
" 2>&1)

if [ "$OUTPUT" = "55" ]; then
  echo "PASS: fibonacci(10) returns 55"
  echo 1 >/logs/verifier/reward.txt
else
  echo "FAIL: expected '55', got '$OUTPUT'"
  echo 0 >/logs/verifier/reward.txt
fi
