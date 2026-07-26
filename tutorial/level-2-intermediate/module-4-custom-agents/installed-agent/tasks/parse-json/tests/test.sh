#!/bin/bash
# Test: verify output.txt contains the extracted value

EXPECTED="42"
ACTUAL=$(cat /home/user/output.txt 2>/dev/null | tr -d '[:space:]')

if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "PASS: output.txt contains the correct value ($EXPECTED)"
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "FAIL: expected '$EXPECTED', got '$ACTUAL'"
    echo "0.0" > /logs/verifier/reward.txt
fi
