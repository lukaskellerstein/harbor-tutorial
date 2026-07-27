#!/bin/bash
# Test: verify the agent explored the environment correctly

REWARD_FILE="/logs/verifier/reward.txt"
SCORE=0
TOTAL=3

# Check 1: listing.txt exists and has content
if [ -f /app/results/listing.txt ] && [ -s /app/results/listing.txt ]; then
    echo "PASS: listing.txt exists and has content"
    SCORE=$((SCORE + 1))
else
    echo "FAIL: listing.txt missing or empty"
fi

# Check 2: config_copy.txt exists and contains JSON
if [ -f /app/results/config_copy.txt ] && grep -q "harbor-demo" /app/results/config_copy.txt; then
    echo "PASS: config_copy.txt contains config data"
    SCORE=$((SCORE + 1))
else
    echo "FAIL: config_copy.txt missing or incorrect"
fi

# Check 3: environment_info.txt exists and has system info
if [ -f /app/results/environment_info.txt ] && [ -s /app/results/environment_info.txt ]; then
    echo "PASS: environment_info.txt exists and has content"
    SCORE=$((SCORE + 1))
else
    echo "FAIL: environment_info.txt missing or empty"
fi

# Calculate reward as fraction
REWARD=$(echo "scale=2; $SCORE / $TOTAL" | bc)
echo "Score: $SCORE/$TOTAL (reward: $REWARD)"
echo "$REWARD" > "$REWARD_FILE"
