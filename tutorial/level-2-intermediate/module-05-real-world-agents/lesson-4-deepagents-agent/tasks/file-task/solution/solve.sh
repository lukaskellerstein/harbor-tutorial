#!/bin/bash
cat <<'EOF' >/app/calculator.py
def add(a: int | float, b: int | float) -> float:
    return float(a + b)

def subtract(a: int | float, b: int | float) -> float:
    return float(a - b)

def multiply(a: int | float, b: int | float) -> float:
    return float(a * b)

def divide(a: int | float, b: int | float) -> float:
    if b == 0:
        return 0.0
    return float(a / b)
EOF

cat <<'EOF' >/app/test_calculator.py
from calculator import add, subtract, multiply, divide

assert add(2, 3) == 5
assert subtract(10, 4) == 6
assert multiply(3, 7) == 21
assert divide(10, 2) == 5
assert divide(1, 0) == 0

print("ALL TESTS PASSED")
EOF

python3 /app/test_calculator.py
