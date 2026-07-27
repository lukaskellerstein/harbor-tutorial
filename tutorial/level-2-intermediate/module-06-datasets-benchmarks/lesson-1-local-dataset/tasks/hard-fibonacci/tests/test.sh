#!/bin/bash
# Test: run fibonacci.py and check output matches expected sequence

EXPECTED="0
1
1
2
3
5
8
13
21
34"

if [ ! -f /workspace/fibonacci.py ]; then
    echo "FAIL: fibonacci.py not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

ACTUAL=$(python3 /workspace/fibonacci.py 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "FAIL: fibonacci.py exited with code $EXIT_CODE"
    echo "Output: $ACTUAL"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# Trim trailing whitespace/newlines for comparison
ACTUAL_TRIMMED=$(echo "$ACTUAL" | sed 's/[[:space:]]*$//')
EXPECTED_TRIMMED=$(echo "$EXPECTED" | sed 's/[[:space:]]*$//')

if [ "$ACTUAL_TRIMMED" = "$EXPECTED_TRIMMED" ]; then
    echo "PASS: fibonacci.py produces correct output"
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "FAIL: incorrect output"
    echo "Expected:"
    echo "$EXPECTED"
    echo "Got:"
    echo "$ACTUAL"
    echo "0.0" > /logs/verifier/reward.txt
fi
