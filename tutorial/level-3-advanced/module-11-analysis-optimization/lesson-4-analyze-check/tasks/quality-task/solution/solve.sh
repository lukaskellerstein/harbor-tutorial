#!/bin/bash
cat > /home/user/calculator.py << 'PYEOF'
def calculate(expr: str) -> str:
    parts = expr.strip().split()
    if len(parts) != 3:
        return "error: invalid expression"
    try:
        left = float(parts[0])
        op = parts[1]
        right = float(parts[2])
    except ValueError:
        return "error: invalid expression"

    if op == "+":
        result = left + right
    elif op == "-":
        result = left - right
    elif op == "*":
        result = left * right
    elif op == "/":
        if right == 0:
            return "error: division by zero"
        result = left / right
    else:
        return "error: invalid expression"

    if result == int(result):
        return str(int(result))
    return str(result)

with open("/home/user/expression.txt") as f:
    expression = f.read().strip()

print(calculate(expression))
PYEOF
