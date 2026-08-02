#!/bin/bash
# Test script for multi-service task
#
# Verifies that the agent successfully:
# 1. Created a user via the API
# 2. The user exists in the database
#
# Writes reward (0 or 1) to /logs/verifier/reward.txt

set -e

mkdir -p /logs/verifier

# Check if the test user exists in the database
RESULT=$(PGPASSWORD=harbor psql -h db -U harbor -d harbordb -t -c \
  "SELECT COUNT(*) FROM users WHERE name='harbor_test_user';")

COUNT=$(echo "$RESULT" | tr -d ' ')

if [ "$COUNT" -ge 1 ]; then
  echo "PASS: User 'harbor_test_user' found in database ($COUNT rows)"
  echo "1" >/logs/verifier/reward.txt
else
  echo "FAIL: User 'harbor_test_user' not found in database"
  echo "0" >/logs/verifier/reward.txt
fi
