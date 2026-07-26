#!/bin/bash
# Test: verify the Python script ran and produced the status code

REWARD_FILE="/logs/verifier/reward.txt"

if [ -f /app/status.txt ] && grep -q "200" /app/status.txt; then
    echo "PASS: status.txt exists and contains 200"
    echo "1" > "$REWARD_FILE"
else
    echo "FAIL: status.txt missing or does not contain 200"
    echo "0" > "$REWARD_FILE"
fi
