#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/csv_stats.py ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: csv_stats.py not found"
  exit 0
fi

ACTUAL=$(python3 /home/user/csv_stats.py 2>/dev/null)

# Check each line separately for partial credit
SCORE=0
TOTAL=4

echo "$ACTUAL" | grep -q "count: 5" && SCORE=$((SCORE + 1))
echo "$ACTUAL" | grep -q "mean: 87.6" && SCORE=$((SCORE + 1))
echo "$ACTUAL" | grep -q "max: 95" && SCORE=$((SCORE + 1))
echo "$ACTUAL" | grep -q "min: 78" && SCORE=$((SCORE + 1))

REWARD=$(echo "scale=2; $SCORE / $TOTAL" | bc)
echo "$REWARD" >/logs/verifier/reward.txt

if [ "$SCORE" -eq "$TOTAL" ]; then
  echo "PASS: All stats correct ($SCORE/$TOTAL)"
else
  echo "PARTIAL: $SCORE/$TOTAL stats correct"
  echo "Got: $ACTUAL"
fi
