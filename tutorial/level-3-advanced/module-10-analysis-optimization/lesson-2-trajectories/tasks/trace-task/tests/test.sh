#!/bin/bash
mkdir -p /logs/verifier
SCORE=0
TOTAL=3

# Check greeting.py
if [ -f /home/user/greeting.py ]; then
    OUTPUT=$(python3 /home/user/greeting.py 2>/dev/null)
    [ "$OUTPUT" = "Hello, Harbor!" ] && SCORE=$((SCORE + 1))
fi

# Check config.json
if [ -f /home/user/config.json ]; then
    python3 -c "
import json
with open('/home/user/config.json') as f:
    d = json.load(f)
assert d['name'] == 'harbor'
assert d['version'] == '1.0'
assert d['enabled'] is True
" 2>/dev/null && SCORE=$((SCORE + 1))
fi

# Check summary.txt
if [ -f /home/user/summary.txt ]; then
    CONTENT=$(cat /home/user/summary.txt | tr -d '\n')
    [ "$CONTENT" = "Setup complete." ] && SCORE=$((SCORE + 1))
fi

REWARD=$(echo "scale=2; $SCORE / $TOTAL" | bc)
echo "$REWARD" > /logs/verifier/reward.txt

if [ "$SCORE" -eq "$TOTAL" ]; then
    echo "PASS: All 3 files created correctly ($SCORE/$TOTAL)"
else
    echo "PARTIAL: $SCORE/$TOTAL files correct"
fi
