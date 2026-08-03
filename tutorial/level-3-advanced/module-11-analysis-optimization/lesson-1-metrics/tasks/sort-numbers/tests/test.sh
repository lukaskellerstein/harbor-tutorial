#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/sort_numbers.py ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: sort_numbers.py not found"
  exit 0
fi

python3 /home/user/sort_numbers.py 2>/dev/null

if [ ! -f /home/user/sorted.txt ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: sorted.txt not found"
  exit 0
fi

EXPECTED=$(printf "3\n17\n42\n55\n99\n")
ACTUAL=$(cat /home/user/sorted.txt)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "1.0" >/logs/verifier/reward.txt
  echo "PASS: Numbers sorted correctly."
else
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: Sorted output does not match expected."
fi
