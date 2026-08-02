#!/bin/bash

# Check if /app/hello.txt exists and contains "Hello, world!"
if [ -f /app/hello.txt ]; then
  content=$(cat /app/hello.txt)
  if [ "$content" = "Hello, world!" ]; then
    echo "PASS: hello.txt contains the correct content"
    echo 1 >/logs/verifier/reward.txt
  else
    echo "FAIL: hello.txt exists but contains '$content' instead of 'Hello, world!'"
    echo 0 >/logs/verifier/reward.txt
  fi
else
  echo "FAIL: hello.txt does not exist"
  echo 0 >/logs/verifier/reward.txt
fi
