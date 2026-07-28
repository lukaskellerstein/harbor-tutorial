#!/bin/bash
# Deliberately writes BOTH reward files with CONFLICTING values, to settle the
# precedence question once and for all.
#
#   reward.txt  -> 0.00   (a deliberate lie)
#   reward.json -> the real per-dimension scores, plus a "reward" roll-up
#
# Harbor checks reward.json FIRST and only falls back to reward.txt when the
# JSON file is absent (src/harbor/verifier/verifier.py). So the trial reports
# the JSON scores and the 0.00 is silently ignored.
#
# The published docs claim the opposite order. The source and Harbor's own unit
# test (test_verify_prefers_reward_json_over_reward_text) say JSON wins.

mkdir -p /logs/verifier

REPORT=/app/report.md

FOUND=0
for SECTION in "## Summary" "## Findings" "## Conclusion"; do
    if grep -qF "$SECTION" "$REPORT" 2>/dev/null; then
        FOUND=$((FOUND + 1))
    fi
done
SECTIONS=$(awk "BEGIN {printf \"%.2f\", $FOUND / 3}")

if head -n 1 "$REPORT" 2>/dev/null | grep -q "^# "; then
    TITLE=1
else
    TITLE=0
fi

if [ -f "$REPORT" ]; then
    WORDS=$(wc -w < "$REPORT")
else
    WORDS=0
fi
if [ "$WORDS" -ge 50 ]; then
    LENGTH=1
else
    LENGTH=0
fi

# The "reward" roll-up. Anything that consumes the one-dimensional convention
# -- `min_reward` gates, `harbor analyze --passing/--failing`, `harbor check`
# -- looks for this exact key. Emit it whenever you also emit named dimensions.
ROLLUP=$(awk "BEGIN {printf \"%.2f\", ($SECTIONS + $TITLE + $LENGTH) / 3}")

echo "sections=$SECTIONS title=$TITLE length=$LENGTH -> reward=$ROLLUP"
echo "(also writing reward.txt = 0.00, which Harbor will ignore)"

echo "0.00" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json <<EOF
{
  "sections": $SECTIONS,
  "title": $TITLE,
  "length": $LENGTH,
  "reward": $ROLLUP
}
EOF
