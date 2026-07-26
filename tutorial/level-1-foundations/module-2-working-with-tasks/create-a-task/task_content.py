"""
File contents for the FizzBuzz task.

Extracted from main.py to keep lesson code under ~200 lines.
"""

INSTRUCTION = """\
Create a Python script at /app/fizzbuzz.py that prints FizzBuzz for numbers 1 through 100.

Rules:
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both 3 and 5, print "FizzBuzz"
- For all other numbers, print the number itself
- Print one value per line
"""

TASK_TOML = """\
version = "1.0"

[task]
name = "tutorial/fizzbuzz"
authors = []
keywords = ["python", "beginner"]

[metadata]
author_name = "Harbor Tutorial"
difficulty = "easy"
category = "programming"
tags = ["python", "loops", "conditionals"]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 120.0

[environment]
build_timeout_sec = 600.0
"""

DOCKERFILE = """\
FROM python:3.12-slim

WORKDIR /app
"""

TEST_SH = """\
#!/bin/bash

# Verify the FizzBuzz solution.
# Write a reward (0 or 1) to /logs/verifier/reward.txt.

mkdir -p /logs/verifier

# Check the script exists
if [ ! -f /app/fizzbuzz.py ]; then
    echo "FAIL: /app/fizzbuzz.py not found"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Run the script and capture output
ACTUAL=$(python /app/fizzbuzz.py 2>/dev/null)

# Spot-check key positions
FAIL=0

check_line() {
    local line_num=$1
    local expected_val=$2
    local actual_val=$(echo "$ACTUAL" | sed -n "${line_num}p")
    if [ "$actual_val" != "$expected_val" ]; then
        echo "FAIL at line $line_num: expected '$expected_val', got '$actual_val'"
        FAIL=1
    fi
}

# Check total line count
ACTUAL_LINES=$(echo "$ACTUAL" | wc -l | tr -d ' ')
if [ "$ACTUAL_LINES" != "100" ]; then
    echo "FAIL: Expected 100 lines, got $ACTUAL_LINES"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Check specific positions
check_line 1 "1"
check_line 3 "Fizz"
check_line 5 "Buzz"
check_line 15 "FizzBuzz"
check_line 30 "FizzBuzz"
check_line 97 "97"
check_line 99 "Fizz"
check_line 100 "Buzz"

if [ "$FAIL" -eq 0 ]; then
    echo "PASS: FizzBuzz output is correct"
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
"""

SOLVE_SH = """\
#!/bin/bash

# Reference solution for the FizzBuzz task.

cat > /app/fizzbuzz.py << 'PYTHON'
for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
PYTHON

echo "FizzBuzz solution created."
"""

# Map of relative paths to file contents
ALL_FILES: dict[str, str] = {
    "instruction.md": INSTRUCTION,
    "task.toml": TASK_TOML,
    "environment/Dockerfile": DOCKERFILE,
    "tests/test.sh": TEST_SH,
    "solution/solve.sh": SOLVE_SH,
}
