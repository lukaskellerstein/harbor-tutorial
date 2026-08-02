#!/bin/bash
# Multi-dimension grading: named scores in reward.json.
#
# Same three checks as the reward-txt task, but each one keeps its own identity
# instead of being averaged away. A trial that scores {sections: 1.0, title: 0,
# length: 1.0} tells you the agent can write but ignores formatting rules --
# a single 0.67 does not.
#
# Note this script writes NO "reward" key. See tasks/reward-precedence for why
# that matters.

mkdir -p /logs/verifier

REPORT=/app/report.md

# --- dimension 1: how many required sections are present -------------------
FOUND=0
for SECTION in "## Summary" "## Findings" "## Conclusion"; do
  if grep -qF "$SECTION" "$REPORT" 2>/dev/null; then
    FOUND=$((FOUND + 1))
  fi
done
SECTIONS=$(awk "BEGIN {printf \"%.2f\", $FOUND / 3}")

# --- dimension 2: does it open with a level-1 title? ------------------------
if head -n 1 "$REPORT" 2>/dev/null | grep -q "^# "; then
  TITLE=1
else
  TITLE=0
fi

# --- dimension 3: is it substantial? ---------------------------------------
# REQUIRED_WORDS arrives from [verifier.env] in task.toml.
if [ -f "$REPORT" ]; then
  WORDS=$(wc -w <"$REPORT")
else
  WORDS=0
fi
if [ "$WORDS" -ge "${REQUIRED_WORDS:-50}" ]; then
  LENGTH=1
else
  LENGTH=0
fi

echo "sections: $FOUND/3 -> $SECTIONS"
echo "title:    $TITLE"
echo "words:    $WORDS (need ${REQUIRED_WORDS:-50}) -> $LENGTH"

# reward.json is just a flat JSON object of {name: number}. No library needed.
cat >/logs/verifier/reward.json <<EOF
{
  "sections": $SECTIONS,
  "title": $TITLE,
  "length": $LENGTH
}
EOF
