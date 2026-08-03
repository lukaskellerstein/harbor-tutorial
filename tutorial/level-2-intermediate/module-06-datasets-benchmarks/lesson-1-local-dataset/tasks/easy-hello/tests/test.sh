#!/bin/bash
# Test: check that hello.txt exists and contains the correct text

if [ -f /workspace/hello.txt ]; then
  content=$(cat /workspace/hello.txt)
  if echo "$content" | grep -q "Hello, Harbor!"; then
    echo "PASS: hello.txt contains 'Hello, Harbor!'"
    echo "1.0" >/logs/verifier/reward.txt
  else
    echo "FAIL: hello.txt does not contain 'Hello, Harbor!'"
    echo "Got: $content"
    echo "0.0" >/logs/verifier/reward.txt
  fi
else
  echo "FAIL: hello.txt not found"
  echo "0.0" >/logs/verifier/reward.txt
fi
