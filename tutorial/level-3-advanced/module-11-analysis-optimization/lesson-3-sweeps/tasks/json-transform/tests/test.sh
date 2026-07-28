#!/bin/bash
mkdir -p /logs/verifier

if [ ! -f /home/user/transform.py ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: transform.py not found"
    exit 0
fi

python3 /home/user/transform.py 2>/dev/null

if [ ! -f /home/user/output.json ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "FAIL: output.json not found"
    exit 0
fi

# Validate with Python for reliable JSON comparison
python3 << 'PYEOF'
import json

with open("/home/user/output.json") as f:
    result = json.load(f)

expected = [
    {"name": "Eve", "age": 22},
    {"name": "Charlie", "age": 25},
    {"name": "Alice", "age": 30},
]

score = 0
total = 3

# Check correct number of results (filtered out under 18)
if len(result) == 3:
    score += 1

# Check sorting by age
ages = [p["age"] for p in result]
if ages == sorted(ages) and all(a >= 18 for a in ages):
    score += 1

# Check exact content
if result == expected:
    score += 1

reward = score / total
with open("/logs/verifier/reward.txt", "w") as f:
    f.write(f"{reward:.2f}\n")

if score == total:
    print(f"PASS: All checks passed ({score}/{total})")
else:
    print(f"PARTIAL: {score}/{total} checks passed")
    print(f"Expected: {expected}")
    print(f"Got: {result}")
PYEOF
