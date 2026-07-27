#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/reverse.py ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: reverse.py not found"
    exit 0
fi

# Test case 1: basic reversal
RESULT1=$(echo -n "harbor" | python3 /home/user/reverse.py 2>/dev/null)
# Test case 2: another string
RESULT2=$(echo -n "hello" | python3 /home/user/reverse.py 2>/dev/null)

PASS=0
TOTAL=2

if [ "$RESULT1" = "robrah" ]; then
    PASS=$((PASS + 1))
    echo "PASS: 'harbor' -> '$RESULT1'"
else
    echo "FAIL: Expected 'robrah', got '$RESULT1'"
fi

if [ "$RESULT2" = "olleh" ]; then
    PASS=$((PASS + 1))
    echo "PASS: 'hello' -> '$RESULT2'"
else
    echo "FAIL: Expected 'olleh', got '$RESULT2'"
fi

# Calculate reward as fraction of tests passed
REWARD=$(echo "scale=1; $PASS / $TOTAL" | bc)
echo "$REWARD" > /logs/verifier/reward.txt
echo "Score: $PASS/$TOTAL (reward: $REWARD)"
