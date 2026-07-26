#!/bin/bash

# This test script verifies the agent's solution and writes a reward.
# Harbor runs this script AFTER the agent finishes.
# The reward must be written to /logs/verifier/reward.txt (a float from 0 to 1).

# Create the verifier output directory
mkdir -p /logs/verifier

# Check if the script exists
if [ ! -f /app/count_words.py ]; then
    echo "FAIL: /app/count_words.py does not exist"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Run the script and capture output
ACTUAL=$(python /app/count_words.py 2>/dev/null)
EXPECTED="13"

echo "Expected word count: $EXPECTED"
echo "Actual output:       $ACTUAL"

if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "PASS: Word count is correct"
    echo 1 > /logs/verifier/reward.txt
else
    echo "FAIL: Word count does not match"
    echo 0 > /logs/verifier/reward.txt
fi
