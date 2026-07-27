#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/fizzbuzz.py ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: fizzbuzz.py not found"
    exit 0
fi

# Expected output for FizzBuzz 1-20
EXPECTED="1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
16
17
Fizz
19
Buzz"

ACTUAL=$(python3 /home/user/fizzbuzz.py 2>/dev/null)

if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "PASS: FizzBuzz output is correct."
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: Output does not match expected FizzBuzz sequence."
    echo "--- Expected ---"
    echo "$EXPECTED"
    echo "--- Got ---"
    echo "$ACTUAL"
fi
