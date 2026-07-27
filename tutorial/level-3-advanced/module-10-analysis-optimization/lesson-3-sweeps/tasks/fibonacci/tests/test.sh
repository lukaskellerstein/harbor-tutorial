#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/fib.py ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: fib.py not found"
    exit 0
fi

EXPECTED=$(printf "0\n1\n1\n2\n3\n5\n8\n13\n21\n34")
ACTUAL=$(python3 /home/user/fib.py 2>/dev/null)

if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "PASS: Fibonacci sequence correct."
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: Output does not match expected Fibonacci sequence."
fi
