#!/bin/bash
if [ -f /app/hello.txt ]; then
  content=$(cat /app/hello.txt)
  if [ "$content" = "Hello from Claude Code!" ]; then
    echo "PASS: hello.txt contains the correct content"
    echo 1 >/logs/verifier/reward.txt
  else
    echo "FAIL: hello.txt contains '$content' instead of 'Hello from Claude Code!'"
    echo 0 >/logs/verifier/reward.txt
  fi
else
  echo "FAIL: hello.txt does not exist"
  echo 0 >/logs/verifier/reward.txt
fi
