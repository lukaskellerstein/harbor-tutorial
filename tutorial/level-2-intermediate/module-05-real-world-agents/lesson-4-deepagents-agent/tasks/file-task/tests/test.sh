#!/bin/bash
if [ ! -f /app/calculator.py ]; then
  echo "FAIL: /app/calculator.py does not exist"
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '/app')
from calculator import add, subtract, multiply, divide

errors = []
if add(2, 3) != 5:
    errors.append('add(2,3) failed')
if subtract(10, 4) != 6:
    errors.append('subtract(10,4) failed')
if multiply(3, 7) != 21:
    errors.append('multiply(3,7) failed')
if divide(10, 2) != 5:
    errors.append('divide(10,2) failed')
if divide(1, 0) != 0:
    errors.append('divide(1,0) failed')

if errors:
    print('FAIL: ' + ', '.join(errors))
else:
    print('PASS')
" 2>&1)

if echo "$OUTPUT" | grep -q "PASS"; then
  echo "PASS: All calculator functions work correctly"
  echo 1 > /logs/verifier/reward.txt
else
  echo "FAIL: $OUTPUT"
  echo 0 > /logs/verifier/reward.txt
fi
