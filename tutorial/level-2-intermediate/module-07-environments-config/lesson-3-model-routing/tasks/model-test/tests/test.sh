#!/bin/bash
# Test: verify result.txt contains the expected text

REWARD_FILE="/logs/verifier/reward.txt"

if [ -f /app/result.txt ] && grep -q "model routing works" /app/result.txt; then
    echo "PASS: result.txt contains expected text"
    echo "1" > "$REWARD_FILE"
else
    echo "FAIL: result.txt missing or incorrect"
    echo "0" > "$REWARD_FILE"
fi
