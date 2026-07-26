#!/bin/bash

# APPROACH 1: Binary test (pass/fail)
#
# This is the simplest testing approach. The reward is either
# 0 (fail) or 1 (pass) -- no partial credit.

mkdir -p /logs/verifier

# Check if the file exists
if [ ! -f /app/greeting.txt ]; then
    echo "FAIL: /app/greeting.txt does not exist"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Check the contents
ACTUAL=$(cat /app/greeting.txt | tr -d '\n')
EXPECTED="Hello, Harbor!"

if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "PASS: File content matches"
    echo 1 > /logs/verifier/reward.txt
else
    echo "FAIL: Expected '$EXPECTED', got '$ACTUAL'"
    echo 0 > /logs/verifier/reward.txt
fi
