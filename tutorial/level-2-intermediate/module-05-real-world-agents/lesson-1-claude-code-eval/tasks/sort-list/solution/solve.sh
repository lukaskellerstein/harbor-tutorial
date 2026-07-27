#!/bin/bash
cat << 'EOF' > /app/sort_numbers.py
with open("/app/numbers.txt") as f:
    numbers = [int(line.strip()) for line in f if line.strip()]
numbers.sort()
with open("/app/sorted.txt", "w") as f:
    for n in numbers:
        f.write(f"{n}\n")
EOF
python3 /app/sort_numbers.py
