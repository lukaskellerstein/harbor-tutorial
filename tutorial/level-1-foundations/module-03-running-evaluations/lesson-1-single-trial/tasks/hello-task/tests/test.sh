#!/bin/bash
# Test script: checks that /home/user/hello.txt contains "Hello, Harbor!"
# Writes reward (0 or 1) to /logs/verifier/reward.txt

mkdir -p /logs/verifier

EXPECTED="Hello, Harbor!"
ACTUAL=$(cat /home/user/hello.txt 2>/dev/null)

if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "1.0" >/logs/verifier/reward.txt
  echo "PASS: hello.txt contains the expected text."
else
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: Expected '$EXPECTED', got '$ACTUAL'"
fi
