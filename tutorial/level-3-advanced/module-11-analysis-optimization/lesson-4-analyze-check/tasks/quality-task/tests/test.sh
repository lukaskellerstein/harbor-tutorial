#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/calculator.py ]; then
  echo "0.0" >/logs/verifier/reward.txt
  echo "FAIL: calculator.py not found"
  exit 0
fi

SCORE=0
TOTAL=5

# Test 1: Basic addition
echo "3 + 5" >/home/user/expression.txt
RESULT=$(python3 /home/user/calculator.py 2>/dev/null)
[ "$RESULT" = "8" ] && SCORE=$((SCORE + 1))

# Test 2: Subtraction
echo "10 - 3" >/home/user/expression.txt
RESULT=$(python3 /home/user/calculator.py 2>/dev/null)
[ "$RESULT" = "7" ] && SCORE=$((SCORE + 1))

# Test 3: Multiplication
echo "4 * 6" >/home/user/expression.txt
RESULT=$(python3 /home/user/calculator.py 2>/dev/null)
[ "$RESULT" = "24" ] && SCORE=$((SCORE + 1))

# Test 4: Division
echo "15 / 4" >/home/user/expression.txt
RESULT=$(python3 /home/user/calculator.py 2>/dev/null)
[ "$RESULT" = "3.75" ] && SCORE=$((SCORE + 1))

# Test 5: Division by zero
echo "5 / 0" >/home/user/expression.txt
RESULT=$(python3 /home/user/calculator.py 2>/dev/null)
[ "$RESULT" = "error: division by zero" ] && SCORE=$((SCORE + 1))

REWARD=$(echo "scale=2; $SCORE / $TOTAL" | bc)
echo "$REWARD" >/logs/verifier/reward.txt

if [ "$SCORE" -eq "$TOTAL" ]; then
  echo "PASS: All tests passed ($SCORE/$TOTAL)"
else
  echo "PARTIAL: $SCORE/$TOTAL tests passed"
fi
