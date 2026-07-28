#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/matrix_mul.py ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: matrix_mul.py not found"
    exit 0
fi

python3 /home/user/matrix_mul.py 2>/dev/null

if [ ! -f /home/user/result.txt ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: result.txt not found"
    exit 0
fi

# Expected result of [[1,2,3],[4,5,6]] x [[7,8],[9,10],[11,12]]
# = [[58,64],[139,154]]
EXPECTED=$(printf "58 64\n139 154\n")
ACTUAL=$(cat /home/user/result.txt)

# Check row by row for partial credit
SCORE=0
TOTAL=2

ROW1=$(echo "$ACTUAL" | head -1 | tr -s ' ')
ROW2=$(echo "$ACTUAL" | tail -1 | tr -s ' ')

[ "$ROW1" = "58 64" ] && SCORE=$((SCORE + 1))
[ "$ROW2" = "139 154" ] && SCORE=$((SCORE + 1))

REWARD=$(echo "scale=2; $SCORE / $TOTAL" | bc)
echo "$REWARD" > /logs/verifier/reward.txt

if [ "$SCORE" -eq "$TOTAL" ]; then
    echo "PASS: Matrix multiplication correct ($SCORE/$TOTAL rows)"
else
    echo "PARTIAL: $SCORE/$TOTAL rows correct"
    echo "Expected:"
    echo "$EXPECTED"
    echo "Got:"
    echo "$ACTUAL"
fi
