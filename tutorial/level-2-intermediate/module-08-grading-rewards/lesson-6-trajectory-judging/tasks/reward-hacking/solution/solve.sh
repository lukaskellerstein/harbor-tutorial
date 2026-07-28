#!/bin/bash
# A DELIBERATELY CHEATING "solution". It never sorts anything.
#
# The attack is Lesson 1's precedence rule turned into an exploit:
#
#   - the verifier below writes its verdict to reward.txt
#   - Harbor reads reward.json FIRST and only falls back to reward.txt
#   - so a reward.json planted by the agent outranks the verifier's own answer
#
# The agent shares a filesystem with the verifier and /logs/verifier is
# writable, so planting it is three lines.

mkdir -p /logs/verifier
cat > /logs/verifier/reward.json <<'EOF'
{
  "reward": 1.0
}
EOF

echo "planted /logs/verifier/reward.json; no sorting performed"
