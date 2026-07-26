#!/bin/bash
# Test: verify primes.py exists and outputs the correct largest prime below 1000

if [ ! -f /home/user/primes.py ]; then
    echo "FAIL: primes.py not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

OUTPUT=$(python3 /home/user/primes.py 2>/dev/null | tr -d '[:space:]')
EXPECTED="997"

if [ "$OUTPUT" = "$EXPECTED" ]; then
    echo "PASS: primes.py correctly outputs $EXPECTED"
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "FAIL: expected '$EXPECTED', got '$OUTPUT'"
    echo "0.0" > /logs/verifier/reward.txt
fi
