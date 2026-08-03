#!/bin/bash
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
