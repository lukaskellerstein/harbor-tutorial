#!/bin/bash
# Single-dimension grading: one float in reward.txt.
#
# Harbor always keys this value as "reward". Whatever nuance the check has --
# three separate section checks, here -- gets flattened into that one number.

mkdir -p /logs/verifier

REPORT=/app/report.md

FOUND=0
for SECTION in "## Summary" "## Findings" "## Conclusion"; do
    if grep -qF "$SECTION" "$REPORT" 2>/dev/null; then
        echo "  found:   $SECTION"
        FOUND=$((FOUND + 1))
    else
        echo "  MISSING: $SECTION"
    fi
done

REWARD=$(awk "BEGIN {printf \"%.2f\", $FOUND / 3}")
echo "sections: $FOUND/3  ->  reward $REWARD"

echo "$REWARD" > /logs/verifier/reward.txt
